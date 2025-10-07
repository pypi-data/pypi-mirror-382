"""
SNID: Supernova Identification
------------------------------

Core SNID pipeline implementing template matching using cross-correlation techniques
to identify the type, age and redshift of supernova spectra.

This implementation follows the original SNID Fortran flow with numbered stages
and includes GMM clustering for outlier rejection and comprehensive statistical analysis.
"""

from __future__ import annotations
import time, logging
import warnings
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Callable
import math  # Added for batch processing

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks, peak_prominences

from .io import (
    read_spectrum, load_templates,
    write_result, write_fluxed_spectrum, write_flattened_spectrum,
    write_correlation, write_parameter_file, generate_output_files
)
from .preprocessing import (
    init_wavelength_grid, get_grid_params,
    medfilt,
    clip_aband, clip_sky_lines, clip_host_emission_lines, pad_to_NW,
    apply_wavelength_mask, log_rebin, fit_continuum, apodize, unflatten_on_loggrid, prep_template
)
from .fft_tools import (
    apply_filter as bandpass,
    overlap, aspart,
    calculate_rms,
    shiftit,
    dtft_drms
)
from .snidtype import (
    determine_best_type, SNIDResult,
    compute_type_fractions,
    compute_subtype_fractions,
    compute_initial_redshift,
)
from .plotting import (
 
    plot_correlation_function, plot_redshift_age,
    plot_type_fractions
)
from snid_sage.shared.exceptions.core_exceptions import SpectrumProcessingError

# Constants
NW = 1024  # Standard number of wavelength bins
MINW = 2500  # Minimum wavelength in Angstroms
MAXW = 10000  # Maximum wavelength in Angstroms

Trace = Dict[str, Any]

# Use centralized logging system if available, fallback to standard logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOG = get_logger('snid.pipeline')
except ImportError:
    _LOG = logging.getLogger("snid.pipeline")

# Check for optimization system
_OPTIMIZATION_AVAILABLE = False
_OPTIMIZATION_ENABLED = False

# Allow disabling optimization via environment variable for debugging
import os
FORCE_DISABLE_OPTIMIZATION = os.environ.get('SNID_DISABLE_OPTIMIZATION', '').lower() in ('1', 'true', 'yes')
FORCE_STANDARD_METHOD = os.environ.get('SNID_FORCE_STANDARD', '').lower() in ('1', 'true', 'yes')

if not FORCE_DISABLE_OPTIMIZATION:
    try:
        from .optimization_integration import optimize_template_loading, is_optimization_enabled
        from .core.integration import integrate_fft_optimization, load_templates_unified

        _OPTIMIZATION_AVAILABLE = True
        _LOG.debug("✅ Optimization integration available")  # Changed to DEBUG level
    except ImportError as e:
        _LOG.debug(f"⚠️ Optimization integration not available: {e}")  # Changed to DEBUG level
        _OPTIMIZATION_AVAILABLE = False
    except Exception as e:
        _LOG.error(f"❌ Error importing optimization: {e}")
        _OPTIMIZATION_AVAILABLE = False
else:
    _LOG.debug("🔧 Optimization disabled via SNID_DISABLE_OPTIMIZATION environment variable")  # Changed to DEBUG level
    _OPTIMIZATION_AVAILABLE = False

# Additional check for forcing standard method even with optimization available
if FORCE_STANDARD_METHOD:
    _LOG.debug("🔧 Forcing standard correlation method via SNID_FORCE_STANDARD environment variable")  # Changed to DEBUG level
    _OPTIMIZATION_AVAILABLE = False

def preprocess_spectrum(
    spectrum_path: Optional[str] = None,
    input_spectrum: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    *,
    # Preprocessing options
    # Step 0a: spike masking (early outlier removal)
    spike_masking: bool = True,
    spike_floor_z: float = 50.0,
    spike_baseline_window: int = 501,
    spike_baseline_width: float | None = None,
    spike_rel_edge_ratio: float = 2.0,
    spike_min_separation: int = 2,
    spike_max_removals: Optional[int] = None,
    spike_min_abs_resid: Optional[float] = None,
    savgol_window: int = 0,
    savgol_fwhm: float = 0.0,
    savgol_order: int = 3,
    aband_remove: bool = False,
    skyclip: bool = False,
    emclip_z: float = -1.0,
    emwidth: float = 40.0,
    wavelength_masks: Optional[List[Tuple[float, float]]] = None,
    apodize_percent: float = 10.0,
    skip_steps: Optional[List[str]] = None,
    verbose: bool = False,
    # Grid handling
    clip_to_grid: bool = True,
    grid_min_wave: Optional[float] = None,
    grid_max_wave: Optional[float] = None,
    min_overlap_angstrom: float = 2000.0,
) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Preprocess a spectrum for SNID analysis.
    
    This function handles all preprocessing steps (0-6) and returns the processed
    spectrum ready for correlation analysis. Can be used standalone or as part
    of the full SNID pipeline.
    
    Parameters
    ----------
    spectrum_path : str, optional
        Path to the input spectrum file (if input_spectrum not provided)
    input_spectrum : tuple of (np.ndarray, np.ndarray), optional
        Input spectrum as (wave, flux) arrays
    savgol_window : int, optional
        Savitzky-Golay filter window size in pixels (0 = no filtering)
    savgol_fwhm : float, optional
        Savitzky-Golay filter FWHM in Angstroms (alternative to window size)
    savgol_order : int, optional
        Savitzky-Golay filter polynomial order
    aband_remove : bool, optional
        Whether to remove telluric A-band
    skyclip : bool, optional
        Whether to clip sky emission lines
    emclip_z : float, optional
        Redshift at which to clip emission lines (-1 to disable)
    emwidth : float, optional
        Width in Angstroms for emission line clipping
    wavelength_masks : list of (float, float) tuples, optional
        Wavelength ranges to mask out
    apodize_percent : float, optional
        Percentage of spectrum ends to apodize
            skip_steps : list of str, optional
        List of preprocessing steps to skip:
        ['clipping', 'savgol_filtering', 'log_rebinning', 'flux_scaling', 
         'continuum_fitting', 'apodization']
    verbose : bool, optional
        Whether to print detailed information
        
    Returns
    -------
    processed_spectrum : dict
        Dictionary containing processed spectrum with keys:
        - 'input_spectrum': {'wave': array, 'flux': array}  # Original input
        - 'log_wave': array  # Log-rebinned wavelength grid
        - 'log_flux': array  # Log-rebinned flux (scaled to mean=1)
        - 'flat_flux': array  # Flattened (continuum-removed) flux
        - 'tapered_flux': array  # Final apodized flux ready for FFT
        - 'continuum': array  # Fitted continuum
        - 'nonzero_mask': slice  # Slice for non-zero region
        - 'left_edge': int, 'right_edge': int  # Edges of valid data
    trace : dict
        Dictionary with intermediate processing steps for debugging
    """
    
    if skip_steps is None:
        skip_steps = []
    
    trace = {}
    
    _LOG.info("="*60)
    _LOG.info("SNID SPECTRUM PREPROCESSING")
    _LOG.info("="*60)
    
    # ============================================================================
    # STEP 0: READ SPECTRUM OR USE PROVIDED INPUT
    # ============================================================================
    if input_spectrum is not None:
        wave, flux = input_spectrum
        _LOG.info("Step 0: Using provided spectrum input")
        _LOG.info(f"  Wavelength range: {wave.min():.1f} - {wave.max():.1f} Å")
        _LOG.info(f"  Number of points: {len(wave)}")
    elif spectrum_path is not None:
        wave, flux = read_spectrum(spectrum_path)
        _LOG.info(f"Step 0: Read spectrum from {spectrum_path}")
        _LOG.info(f"  Wavelength range: {wave.min():.1f} - {wave.max():.1f} Å")
        _LOG.info(f"  Number of points: {len(wave)}")
    else:
        raise ValueError("Either spectrum_path or input_spectrum must be provided")
    
    # Store original input
    input_spec = {'wave': wave.copy(), 'flux': flux.copy()}
    trace["step0_wave"], trace["step0_flux"] = wave.copy(), flux.copy()

    # ------------------------------------------------------------------------
    # STEP 0b: VALIDATE/CLIP TO GRID RANGE BEFORE FURTHER PROCESSING
    # ------------------------------------------------------------------------
    # Determine grid bounds to use for validation
    gmin = float(grid_min_wave) if grid_min_wave is not None else float(MINW)
    gmax = float(grid_max_wave) if grid_max_wave is not None else float(MAXW)

    wmin = float(np.min(wave)) if len(wave) else np.nan
    wmax = float(np.max(wave)) if len(wave) else np.nan

    if not np.isfinite(wmin) or not np.isfinite(wmax):
        raise SpectrumProcessingError("Input spectrum has invalid wavelength bounds")

    # Check overlap with the optical grid
    has_overlap = (wmax >= gmin) and (wmin <= gmax)
    if not has_overlap:
        msg = (
            f"Spectrum wavelength range {wmin:.1f}-{wmax:.1f} Å is completely outside "
            f"the optical grid {gmin:.0f}-{gmax:.0f} Å."
        )
        _LOG.error(msg)
        raise SpectrumProcessingError(msg)

    # Require minimum overlap with the grid in Angstroms
    overlap_angstrom = max(0.0, min(wmax, gmax) - max(wmin, gmin))
    if overlap_angstrom < float(min_overlap_angstrom):
        msg = (
            f"Insufficient overlap with optical grid: only {overlap_angstrom:.1f} Å "
            f"(< {float(min_overlap_angstrom):.0f} Å required)."
        )
        _LOG.error(msg)
        raise SpectrumProcessingError(msg)

    # Clip to grid if spectrum extends beyond bounds
    if clip_to_grid and ((wmin < gmin) or (wmax > gmax)):
        mask = (wave >= gmin) & (wave <= gmax)
        prev_len = len(wave)
        wave = wave[mask]
        flux = flux[mask]
        _LOG.warning(
            f"Step 0b: Clipped spectrum to grid bounds {gmin:.0f}-{gmax:.0f} Å "
            f"(kept {len(wave)}/{prev_len} points)"
        )
        trace["step0b_clipped_to_grid"] = True
        trace["step0b_wave"], trace["step0b_flux"] = wave.copy(), flux.copy()
    else:
        trace["step0b_clipped_to_grid"] = False
    
    # ============================================================================
    # STEP 0a: EARLY SPIKE MASKING (optional default)
    # ============================================================================
    # Allow skipping via skip_steps or parameter toggle
    if ("spike_masking" not in skip_steps) and spike_masking:
        try:
            from .preprocessing import apply_spike_mask
            wave, flux, spike_info = apply_spike_mask(
                wave,
                flux,
                floor_z=spike_floor_z,
                baseline_window=spike_baseline_window,
                baseline_width=spike_baseline_width,
                rel_edge_ratio=spike_rel_edge_ratio,
                min_separation=spike_min_separation,
                max_removals=spike_max_removals,
                min_abs_resid=spike_min_abs_resid,
            )
            _LOG.info(
                f"Step 0a: Spike masking removed {len(spike_info.get('removed_indices', []))} spikes"
            )
            trace["step0a_removed_indices"] = spike_info.get("removed_indices", np.array([], int))
            trace["step0a_wave"], trace["step0a_flux"] = wave.copy(), flux.copy()
        except Exception as e:
            _LOG.warning(f"Step 0a: Spike masking skipped due to error: {e}")
    else:
        _LOG.info("Step 0a: Spike masking skipped")

    # ============================================================================
    # STEP 1: CLIPPING IN LINEAR WAVELENGTH
    # ============================================================================
    if "clipping" not in skip_steps:
        if aband_remove:
            wave, flux = clip_aband(wave, flux)
            _LOG.debug("    Applied A-band removal")
        if skyclip:
            wave, flux = clip_sky_lines(wave, flux, emwidth)
            _LOG.debug("    Applied sky line clipping")
        if emclip_z >= 0:
            wave, flux = clip_host_emission_lines(wave, flux, emclip_z, emwidth)
            _LOG.debug(f"    Applied emission line clipping at z={emclip_z}")
        if wavelength_masks:
            wave, flux = apply_wavelength_mask(wave, flux, wavelength_masks)
            _LOG.debug(f"    Applied {len(wavelength_masks)} wavelength masks")
        _LOG.info("Step 1: Applied clipping operations")
    else:
        _LOG.info("Step 1: Skipped clipping operations")
    
    trace["step1_wave"], trace["step1_flux"] = wave.copy(), flux.copy()

    # ============================================================================
    # STEP 2: SAVITZKY-GOLAY SMOOTHING (replaces median filtering)
    # ============================================================================
    if "savgol_filtering" not in skip_steps:
        if savgol_fwhm > 0:
            from .preprocessing import savgol_filter_wavelength
            flux = savgol_filter_wavelength(wave, flux, savgol_fwhm, savgol_order)
            filter_description = f"Savitzky-Golay smoothing (wavelength FWHM={savgol_fwhm}Å, order={savgol_order})"
        elif savgol_window > 0:
            from .preprocessing import savgol_filter_fixed
            flux = savgol_filter_fixed(flux, savgol_window, savgol_order)
            filter_description = f"Savitzky-Golay smoothing (window={savgol_window} pixels, order={savgol_order})"
        else:
            filter_description = "no filtering applied"
        _LOG.info(f"Step 2: Applied {filter_description}")
    else:
        _LOG.info("Step 2: Skipped smoothing")
    
    trace["step2_wave"], trace["step2_flux"] = wave.copy(), flux.copy()

    # ============================================================================
    # STEP 3: LOG-WAVELENGTH REBINNING
    # ============================================================================
    if "log_rebinning" not in skip_steps:
        init_wavelength_grid(num_points=NW, min_wave=MINW, max_wave=MAXW)
        NW_grid, W0, W1, DWLOG_grid = get_grid_params()
        log_wave, log_flux = log_rebin(wave, flux)
        _LOG.info("Step 3: Performed log-wavelength rebinning")
        if verbose:
            _LOG.info(f"    Grid parameters: NW={NW_grid}, W0={W0:.1f}, W1={W1:.1f}, DWLOG={DWLOG_grid:.6f}")
    else:
        # Assume input is already log-rebinned, but still initialize grid
        init_wavelength_grid(num_points=NW, min_wave=MINW, max_wave=MAXW)
        NW_grid, W0, W1, DWLOG_grid = get_grid_params()
        log_wave, log_flux = wave.copy(), flux.copy()
        _LOG.info("Step 3: Skipped log-wavelength rebinning (assuming input is pre-rebinned)")
    
    trace["step3_wave"], trace["step3_flux"] = log_wave.copy(), log_flux.copy()

    # ============================================================================
    # STEP 4: RESCALE FLUX TO MEAN=1
    # ============================================================================
    if "flux_scaling" not in skip_steps:
        mask = log_flux > 0
        if np.any(mask):
            mean_flux = np.mean(log_flux[mask])
            if mean_flux > 0:
                log_flux /= mean_flux
                _LOG.info(f"Step 4: Rescaled flux to mean=1 (original mean: {mean_flux:.3f})")
            else:
                _LOG.info("Step 4: Warning - mean flux is zero or negative, skipping scaling")
        else:
            _LOG.info("Step 4: Warning - no positive flux values found, skipping scaling")
    else:
        _LOG.info("Step 4: Skipped flux scaling")
    
    trace["step4_wave"], trace["step4_flux"] = log_wave.copy(), log_flux.copy()

    # ============================================================================
    # STEP 5: CONTINUUM FITTING -> FLATTENED SPECTRUM
    # ============================================================================
    if "continuum_fitting" not in skip_steps:
        flat_flux, cont = fit_continuum(
            log_flux,
            method="spline"
        )
        _LOG.info("Step 5: Fitted and removed continuum")
        if verbose:
            cont_mean = np.mean(cont[cont > 0]) if np.any(cont > 0) else 0
            _LOG.info(f"    Mean continuum level: {cont_mean:.3f}")
    else:
        # Assume input is already flattened
        flat_flux = log_flux.copy()
        cont = np.ones_like(log_flux)  # Dummy continuum
        _LOG.info("Step 5: Skipped continuum fitting (assuming input is pre-flattened)")
    
    trace["step5_flux"], trace["step5_cont"] = flat_flux.copy(), cont.copy()

    # Find valid (non-zero) region of the spectrum
    # For continuum-subtracted spectra, negative values are valid
    # We should only exclude true zeros/NaNs, not negative values
    valid_mask = (log_flux != 0) & np.isfinite(log_flux)
    if np.any(valid_mask):
        left_edge = np.argmax(valid_mask)
        right_edge = len(log_flux) - 1 - np.argmax(valid_mask[::-1])
    else:
        left_edge = 0
        right_edge = len(log_flux) - 1

    # ============================================================================
    # STEP 6: APODIZE THE ENDS
    # ============================================================================
    if "apodization" not in skip_steps:
        # For continuum-subtracted spectra, negative values are valid
        # We should only exclude true zeros/NaNs, not negative values
        valid_indices = np.where((flat_flux != 0) & np.isfinite(flat_flux))[0]
        if valid_indices.size:
            l1, l2 = valid_indices[0], valid_indices[-1]
        else:
            l1, l2 = 0, len(flat_flux) - 1
        tapered_flux = apodize(flat_flux, l1, l2, percent=apodize_percent)
        _LOG.info(f"Step 6: Applied apodization ({apodize_percent}% taper) to spectrum ends")
        if verbose:
            _LOG.info(f"    Apodization range: indices {l1} to {l2}")
    else:
        tapered_flux = flat_flux.copy()
        _LOG.info("Step 6: Skipped apodization")
    
    trace["step6_flux"] = tapered_flux.copy()

    # ============================================================================
    # PREPARE OUTPUT
    # ============================================================================
    processed_spectrum = {
        'input_spectrum': input_spec,
        'log_wave': log_wave,
        'log_flux': log_flux,  # Scaled flux on log grid
        'flat_flux': flat_flux,  # Continuum-removed flux
        'tapered_flux': tapered_flux,  # Final flux ready for FFT
        'continuum': cont,
        'nonzero_mask': slice(left_edge, right_edge + 1),
        'left_edge': left_edge,
        'right_edge': right_edge,
        'grid_params': {
            'NW': NW_grid,
            'W0': W0,
            'W1': W1,
            'DWLOG': DWLOG_grid
        }
    }
    
    _LOG.info("="*60)
    _LOG.info("PREPROCESSING COMPLETE")
    _LOG.info(f"  Input points: {len(input_spec['wave'])}")
    _LOG.info(f"  Log-rebinned points: {len(log_wave)}")
    _LOG.info(f"  Valid data range: indices {left_edge} to {right_edge}")
    _LOG.info(f"  Wavelength range: {log_wave[left_edge]:.1f} - {log_wave[right_edge]:.1f} Å")
    _LOG.info("="*60)
    
    return processed_spectrum, trace


def _process_template_peaks(
    valid_peaks_indices: List[int],
    Rz: np.ndarray,
    tplate: np.ndarray,
    tpl: Dict[str, Any],
    tapered_flux: np.ndarray,
    log_wave: np.ndarray,
    NW_grid: int,
    DWLOG_grid: float,
    k1: int, k2: int, k3: int, k4: int,
    lapmin: float,
    rlapmin: float,
    zmin: float,
    zmax: float,
    peak_window_size: int,
    cont: np.ndarray,
    left_edge: int,
    right_edge: int,
    # NEW: Optional pre-computed template data for optimization
    template_fft: Optional[np.ndarray] = None,
    template_rms: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Process peaks found in correlation for a single template.
    
    This function handles the common peak processing logic used by both
    optimized and standard correlation methods.
    """
    from .fft_tools import shiftit, overlap, calculate_rms, aspart
    from .preprocessing import apodize, pad_to_NW
    
    matches = []
    
    for i0 in valid_peaks_indices:
        # Get indices for fitting around peak
        idx_fit = np.arange(i0-2, i0+3) % NW_grid
        y_fit = Rz[idx_fit]
        
        # Fit quadratic to peak region
        try:
            a_p, b_p, c_p = np.polyfit(idx_fit.astype(float), y_fit, 2)
            
            if abs(a_p) < 1e-12:
                ctr_p = float(i0)
                hgt_p = Rz[i0]
            else:
                ctr_p = -b_p / (2*a_p)
                hgt_p = a_p*ctr_p**2 + b_p*ctr_p + c_p

            lag_for_shifting_template = ctr_p - NW_grid//2
            
            # First shift template to this redshift
            tpl_shifted = shiftit(tplate, lag_for_shifting_template)
            
            # Get overlap region
            (t0, t1), (d0, d1), (ov_start, ov_end), fractional_lap = overlap(tpl_shifted, tapered_flux, log_wave)
            
            if fractional_lap <= 0:
                continue
                
            lap = fractional_lap 
            lpeak = lap * DWLOG_grid * NW_grid

            if lap < lapmin:
                continue

            # Trim both arrays to overlapping region and prepare for FFT
            start_trim = max(t0, d0)
            end_trim = min(t1, d1)
            
            if end_trim <= start_trim:
                continue
            
            work_d = tapered_flux[start_trim:end_trim + 1].copy()
            work_t = tpl_shifted[start_trim:end_trim + 1].copy()
            
            if len(work_d) == 0 or len(work_t) == 0:
                continue
            
            # Apodize the trimmed regions
            apodize_percent = 10.0  # Default value
            work_d = apodize(work_d, 0, len(work_d) - 1, percent=apodize_percent)
            work_t = apodize(work_t, 0, len(work_t) - 1, percent=apodize_percent)
            
            # Pad to NW
            work_d = pad_to_NW(work_d, NW_grid)
            work_t = pad_to_NW(work_t, NW_grid)
            
            # Calculate new FFTs and RMS values
            dtft_peak = np.fft.fft(work_d)
            ttft_peak = np.fft.fft(work_t)
            
            drms_peak = calculate_rms(dtft_peak, k1, k2, k3, k4)
            trms_peak = calculate_rms(ttft_peak, k1, k2, k3, k4)
            
            if drms_peak == 0 or trms_peak == 0:
                continue

            # Calculate correlation on trimmed spectra
            cross_power_peak = dtft_peak * np.conj(ttft_peak)
            cspec_filtered_peak = bandpass(cross_power_peak, k1, k2, k3, k4)
            ccf_peak = np.fft.ifft(cspec_filtered_peak).real
            Rz_peak = np.roll(ccf_peak, NW_grid//2)
            if drms_peak * trms_peak > 0:
                Rz_peak /= (NW_grid * drms_peak * trms_peak)

            # Find peak in trimmed correlation
            mid = NW_grid // 2
            search_radius = peak_window_size
            search_start = max(0, mid - search_radius)
            search_end = min(NW_grid, mid + search_radius + 1)
            window = Rz_peak[search_start:search_end]
            if not window.size:
                continue
                
            peak_idx = search_start + np.argmax(window)
            
            # Calculate prominence of the refined peak (second-pass)
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', message='some peaks have a prominence of 0')
                    prom_vals = peak_prominences(Rz_peak, [peak_idx])[0]
                refined_prominence = float(prom_vals[0]) if len(prom_vals) > 0 else 0.0
            except Exception:
                refined_prominence = 0.0
            
            # Get indices for fitting around peak
            idx_fit = np.arange(peak_idx-2, peak_idx+3) % NW_grid
            y_fit = Rz_peak[idx_fit]
            
            try:
                # Fit parabola to points around peak
                a_p, b_p, c_p = np.polyfit(idx_fit.astype(float), y_fit, 2)
                
                if abs(a_p) < 1e-12:
                    ctr_p = float(peak_idx)
                    hgt_p = Rz_peak[peak_idx]
                else:
                    ctr_p = -b_p / (2*a_p)
                    hgt_p = a_p*ctr_p**2 + b_p*ctr_p + c_p
                    
                    # PATCH: Validate quadratic fit to prevent unrealistic extrapolation
                    # If fitted center is too far from actual peak, use direct peak values
                    max_allowed_offset = peak_window_size  # Allow at most the search window size
                    if abs(ctr_p - peak_idx) > max_allowed_offset:
                        _LOG.debug(f"Quadratic fit extrapolated too far: center={ctr_p:.1f}, peak={peak_idx}, "
                                 f"offset={abs(ctr_p - peak_idx):.1f} > {max_allowed_offset}. Using direct peak values.")
                        ctr_p = float(peak_idx)
                        hgt_p = Rz_peak[peak_idx]
                    
                    # Also check for unreasonably high peak heights (more than 10x the original)
                    original_height = Rz_peak[peak_idx]
                    if hgt_p > 10 * original_height:
                        _LOG.debug(f"Quadratic fit produced unrealistic height: fitted={hgt_p:.3f}, "
                                 f"original={original_height:.3f}. Using original height.")
                        ctr_p = float(peak_idx)
                        hgt_p = original_height
                
                # Calculate lag relative to zero-lag position (mid)
                peak_lag = ctr_p - mid
                
                # Calculate final redshift estimate
                final_lag = lag_for_shifting_template + peak_lag
                z_est = np.exp(final_lag * DWLOG_grid) - 1.0
                
                # Check if redshift is within allowed range
                if z_est < zmin or z_est > zmax:
                    continue
                
                # Width calculation from parabola fit
                if a_p < 0:  # Check if it's a maximum
                    # Ensure we don't take sqrt of negative number
                    sqrt_arg = -hgt_p / (2 * a_p)
                    if sqrt_arg >= 0:
                        width = np.sqrt(sqrt_arg)  # Gaussian σ in pixel units
                        fwhm_pix = 2.355 * width   # Convert σ → FWHM
                        z_width = fwhm_pix * DWLOG_grid  # Δz (small-angle approx)
                    else:
                        width = 0.0
                        z_width = 0.0
                else:
                    width = 0.0
                    z_width = 0.0
                
                # Calculate R value and final rlap (using the same logic as original SNID)
                arms_raw, _ = aspart(cross_power_peak, k1, k2, k3, k4, peak_lag)
                arms_norm = arms_raw / (NW_grid * drms_peak * trms_peak)

                if arms_norm > 0:
                    r_value = hgt_p / (2 * arms_norm)
                else:
                    r_value = 0.0

                rlap = r_value * lpeak
                
                if rlap < rlapmin:
                    continue
                
                # Calculate formal redshift error using canonical SNID formula
                zk = 3.0/8.0  # Canonical factor from original SNID (0.375)
                if r_value > 0 and lap > 0:
                    formal_z_error = zk * z_width / (1.0 + r_value)
                else:
                    formal_z_error = z_width if z_width > 0 else 0.0

                # Prepare spectra data for plotting (required by GUI plotting system)
                # Use the same approach as the original working code - global spectrum edges
                plot_wave = log_wave[left_edge:right_edge+1]
                plot_template_flat = tpl_shifted[left_edge:right_edge+1]
                
                # For flux view, reconstruct from flattened: (flat + 1) * continuum
                plot_template_flux = (plot_template_flat + 1.0) * cont[left_edge:right_edge+1]

                # Create match object (matching original SNID structure)
                match = {
                    'template': tpl,
                    'rlap': rlap,
                    'lag': final_lag,
                    'redshift': z_est,
                    'redshift_error': formal_z_error,
                    'r': r_value,
                    'width': z_width,
                    'height': hgt_p,
                    'lap': lap,
                    'prominence': refined_prominence,
                    'type': tpl.get('type', ''),
                    'age': tpl.get('age', 0),
                    'name': tpl.get('name', ''),
                    'median_wave': tpl.get('median_wave', 0),
                    'slope': tpl.get('slope', 0),
                    'position': peak_idx,
                    'normalized_height': hgt_p,
                    'processed_flux': plot_template_flat,  # For legacy plotting compatibility
                    'spectra': {
                        'flux': {
                            'wave': plot_wave,
                            'flux': plot_template_flux
                        },
                        'flat': {
                            'wave': plot_wave,
                            'flux': plot_template_flat
                        }
                    },
                    'correlation_data': {
                        'correlation': Rz_peak,
                        'center': ctr_p,
                        'drms': drms_peak,
                        'trms': trms_peak
                    }
                }
                
                matches.append(match)
                
            except Exception as fit_error:
                _LOG.debug(f"Error in quadratic fit for template {tpl.get('name', 'unknown')}: {fit_error}")
                continue
                
        except Exception as initial_fit_error:
            _LOG.debug(f"Error in initial quadratic fit for template {tpl.get('name', 'unknown')}: {initial_fit_error}")
            continue
    
    return matches


# ============================================================================
# FORCED REDSHIFT ANALYSIS FUNCTIONS
# ============================================================================

def _run_forced_redshift_analysis_optimized(
    templates_dir: str,
    type_filter: Optional[List[str]], 
    template_filter: Optional[List[str]], 
    exclude_templates: Optional[List[str]],
    age_range: Optional[Tuple[float, float]],
    tapered_flux: np.ndarray, 
    dtft: np.ndarray, 
    drms: float,
    left_edge: int, 
    right_edge: int,
    forced_redshift: float, 
    NW_grid: int, 
    DWLOG_grid: float,
    k1: int, k2: int, k3: int, k4: int,
    lapmin: float, 
    rlapmin: float, 
    zmin: float, 
    zmax: float,
    log_wave: np.ndarray,
    cont: np.ndarray,
    report_progress: Callable[[str, Optional[float]], None]
) -> List[Dict[str, Any]]:
    """
    OPTIMIZED forced redshift analysis using vectorized FFT correlation.
    
    This function uses the same optimizations as normal analysis but skips the redshift search,
    making it significantly faster while maintaining the same quality and template handling.
    """
    import math
    import time
    from .fft_tools import shiftit, overlap, calculate_rms, aspart, apply_filter as bandpass, dtft_drms
    from .preprocessing import apodize, pad_to_NW
    from .core.integration import load_templates_unified, integrate_fft_optimization
    from .core.config import SNIDConfig
    
    matches = []
    
    # ============================================================================
    # VALIDATE FORCED REDSHIFT PARAMETERS
    # ============================================================================
    
    # Validate forced redshift value
    if forced_redshift < -0.1 or forced_redshift > 3.0:
        raise ValueError(f"Forced redshift z={forced_redshift:.6f} is outside valid range [-0.1, 3.0]")
    
    if forced_redshift < 0 and forced_redshift < -0.01:
        _LOG.warning(f"Forced redshift z={forced_redshift:.6f} is negative and quite large - this may indicate an error")
    
    # Calculate the lag corresponding to the forced redshift
    try:
        forced_lag = np.log(1 + forced_redshift) / DWLOG_grid
    except Exception as e:
        raise ValueError(f"Failed to calculate lag for forced redshift z={forced_redshift:.6f}: {e}")
    
    _LOG.info(f"🎯 OPTIMIZED forced redshift z={forced_redshift:.6f} corresponds to lag={forced_lag:.3f}")
    
    # ============================================================================
    # LOAD TEMPLATES (SAME AS NORMAL ANALYSIS)
    # ============================================================================
    
    # Use unified storage for loading templates (same as normal analysis)
    try:
        # Default behavior: exclude Galaxy templates from forced analysis unless explicitly requested
        effective_type_filter = type_filter
        if not effective_type_filter:
            effective_type_filter = [
                # Include all known main types except Galaxy/NotSN flat galaxy aliases
                'Ia', 'Ib', 'Ic', 'II', 'SLSN', 'LFBOT', 'TDE', 'KN', 'GAP', 'Star', 'AGN'
            ]
        templates = load_templates_unified(templates_dir, type_filter=effective_type_filter, template_names=template_filter, exclude_templates=exclude_templates)
        _LOG.info(f"✅ Loaded {len(templates)} templates using UNIFIED STORAGE for forced redshift analysis")
    except Exception as e:
        _LOG.warning(f"Unified storage failed in forced analysis, falling back to legacy loader: {e}")
        from .io import load_templates
        templates, _ = load_templates(templates_dir, flatten=True)
        
        # Apply template filtering to legacy templates
        if template_filter:
            templates = [t for t in templates if t.get('name', '') in template_filter]
            _LOG.info(f"Applied template filter: {len(templates)} templates remaining")
        elif exclude_templates:
            original_count = len(templates)
            templates = [t for t in templates if t.get('name', '') not in exclude_templates]
            _LOG.info(f"Excluded {original_count - len(templates)} templates: {len(templates)} remaining")
        
        _LOG.info(f"✅ Loaded {len(templates)} templates using STANDARD method for forced redshift analysis")
    
    if not templates:
        _LOG.error("No templates loaded for forced redshift analysis")
        return []

    # ============================================================================
    # APPLY AGE FILTERING (SAME AS NORMAL ANALYSIS)
    # ============================================================================
    original_count = len(templates)
    
    if age_range is not None:
        age_min, age_max = age_range
        templates = [t for t in templates if age_min <= t.get('age', 0) <= age_max]
        _LOG.info(f"Age filtering for forced analysis: {original_count} -> {len(templates)} templates")

    # ============================================================================
    # CHECK FOR VECTORIZED FFT OPTIMIZATION (SAME AS NORMAL ANALYSIS)
    # ============================================================================
    
    use_vectorized = True  # Default to optimized method
    
    try:
        # Create a configuration object for optimization settings
        config = SNIDConfig(use_vectorized_fft=use_vectorized)
        optimization_available = True
        _LOG.info(f"🚀 Vectorized FFT optimization available for forced redshift analysis")
        
    except ImportError:
        optimization_available = False
        use_vectorized = False
        _LOG.warning(f"Vectorized FFT optimization not available, falling back to legacy method")

    # ============================================================================
    # GROUP TEMPLATES BY TYPE (SAME AS NORMAL ANALYSIS)
    # ============================================================================
    
    # Group templates by type for better progress reporting and memory efficiency
    templates_by_type = {}
    for template in templates:
        sn_type = template.get('type', 'Unknown')
        if sn_type not in templates_by_type:
            templates_by_type[sn_type] = []
        templates_by_type[sn_type].append(template)
    
    _LOG.info(f"🔄 Processing {len(templates_by_type)} supernova types: {list(templates_by_type.keys())}")
    
    # Calculate total templates and track progress
    total_templates = len(templates)
    processed_templates = 0
    
    # Create processing order: Ia first, all II* second, then the rest (same as normal)
    ordered_types = []
    if 'Ia' in templates_by_type:
        ordered_types.append('Ia')
    # Add any type that starts with "II" (e.g., II, II-P, IIb ...)
    ordered_types.extend([t for t in templates_by_type.keys() if t.startswith('II') and t not in ordered_types])
    # Finally add the remaining types preserving original insertion order
    ordered_types.extend([t for t in templates_by_type.keys() if t not in ordered_types])

    _LOG.info(f"🔄 Processing order for forced redshift: {ordered_types}")

    # Track performance for comparison
    start_time = time.time()

    # ============================================================================
    # PROCESS EACH TYPE WITH OPTIMIZED METHOD
    # ============================================================================
    
    for type_idx, sn_type in enumerate(ordered_types):
        type_templates = templates_by_type[sn_type]

        # Decide batching strategy (same as normal analysis)
        batch_parts = 1
        if sn_type == 'Ia':
            batch_parts = 4  # Split Type Ia into 4 batches
        elif sn_type.startswith('II'):
            batch_parts = 2  # Split all Type II* into 2 batches

        if batch_parts > 1:
            batch_size = math.ceil(len(type_templates) / batch_parts)
            batches = [type_templates[i:i + batch_size] for i in range(0, len(type_templates), batch_size)]
        else:
            batches = [type_templates]

        _LOG.info(f"🔄 Type {sn_type}: {len(type_templates)} templates split into {len(batches)} batch(es) (forced z={forced_redshift:.6f})")

        # Process each batch
        for batch_idx, batch_templates in enumerate(batches, start=1):
            # Progress update before processing batch
            batch_start_progress = (processed_templates / total_templates) * 100
            report_progress(f"Processing {sn_type} batch {batch_idx}/{len(batches)} (forced z={forced_redshift:.6f})", batch_start_progress)

            # Track time for this batch
            batch_start_time = time.time()

            # ========================================================================
            # USE VECTORIZED FFT OPTIMIZATION IF AVAILABLE (SAME AS NORMAL ANALYSIS)
            # ========================================================================
            
            batch_matches = []
            
            if optimization_available and use_vectorized and len(batch_templates) > 5:
                try:
                    # Use optimized vectorized correlation for the batch
                    _LOG.debug(f"Using vectorized FFT optimization for {len(batch_templates)} templates in {sn_type} batch {batch_idx}")
                    correlator = integrate_fft_optimization(batch_templates, k1, k2, k3, k4, config=config)
                    correlation_results = correlator.correlate_snid_style(dtft, drms)
                    
                    if not correlation_results:
                        _LOG.warning(f"Vectorized correlation returned no results for {sn_type} batch {batch_idx}")
                        raise RuntimeError("No correlation results from vectorized method")
                    
                    # Process correlation results for forced redshift
                    for template_name, corr_result in correlation_results.items():
                        template_data = corr_result['template']
                        template_meta = template_data.metadata
                        template_rms = corr_result['template_rms']
                        
                        if drms <= 0 or template_rms <= 0:
                            continue
                        
                        try:
                            # Get template flux
                            tplate = template_meta.get('flux', None)
                            if tplate is None or len(tplate) != NW_grid:
                                continue
                            
                            # FORCE: Directly shift template to the forced redshift
                            tpl_shifted = shiftit(tplate, forced_lag)
                            
                            # Get overlap region
                            (t0, t1), (d0, d1), (ov_start, ov_end), fractional_lap = overlap(tpl_shifted, tapered_flux, log_wave)
                            
                            if fractional_lap <= 0:
                                continue
                                
                            lap = fractional_lap 
                            lpeak = lap * DWLOG_grid * NW_grid

                            if lap < lapmin:
                                continue

                            # Process the forced redshift match using the optimized correlation
                            match_info = _process_forced_redshift_match(
                                template_meta, tpl_shifted, tapered_flux, log_wave, cont,
                                forced_redshift, forced_lag, dtft, drms, 
                                NW_grid, DWLOG_grid, k1, k2, k3, k4,
                                lapmin, rlapmin, left_edge, right_edge,
                                lap, lpeak, corr_result['correlation']
                            )
                            
                            if match_info is not None:
                                batch_matches.append(match_info)
                                
                        except Exception as e:
                            _LOG.warning(f"Error processing template {template_name} with vectorized forced redshift: {e}")
                            continue
                            
                    _LOG.debug(f"Vectorized processing found {len(batch_matches)} matches for {sn_type} batch {batch_idx}")
                    
                except Exception as e:
                    _LOG.warning(f"Vectorized forced redshift failed for {sn_type} batch {batch_idx}: {e}")
                    _LOG.warning("Falling back to legacy method for this batch")
                    use_vectorized = False
            
            # Fallback to legacy method if vectorized fails or not available
            if not optimization_available or not use_vectorized or len(batch_templates) <= 5:
                # Legacy template-by-template processing
                for template_idx, tpl in enumerate(batch_templates):
                    try:
                        # Get template flux (ensuring it's not None and has correct size)
                        tplate = tpl.get('flux', None)
                        if tplate is None or len(tplate) != NW_grid:
                            continue
                        
                        # Use pre-computed FFT if available (same optimization as normal analysis)
                        if tpl.get('is_log_rebinned', False) and 'pre_computed_fft' in tpl:
                            ttft = tpl['pre_computed_fft']
                            trms = calculate_rms(ttft, k1, k2, k3, k4)
                        else:
                            ttft, trms = dtft_drms(tplate, 0.0, 0, NW_grid-1, k1, k2, k3, k4)
                        
                        if drms <= 0 or trms <= 0:
                            continue

                        # FORCE: Directly shift template to the forced redshift
                        tpl_shifted = shiftit(tplate, forced_lag)
                        
                        # Get overlap region
                        (t0, t1), (d0, d1), (ov_start, ov_end), fractional_lap = overlap(tpl_shifted, tapered_flux, log_wave)
                        
                        if fractional_lap <= 0:
                            continue
                            
                        lap = fractional_lap 
                        lpeak = lap * DWLOG_grid * NW_grid

                        if lap < lapmin:
                            continue

                        # Calculate correlation for forced redshift
                        cross_power = dtft * np.conj(ttft)
                        cspec_filtered = bandpass(cross_power, k1, k2, k3, k4)
                        ccf = np.fft.ifft(cspec_filtered).real
                        correlation = np.roll(ccf, NW_grid//2) / (NW_grid * drms * trms)

                        # Process the forced redshift match
                        match_info = _process_forced_redshift_match(
                            tpl, tpl_shifted, tapered_flux, log_wave, cont,
                            forced_redshift, forced_lag, dtft, drms, 
                            NW_grid, DWLOG_grid, k1, k2, k3, k4,
                            lapmin, rlapmin, left_edge, right_edge,
                            lap, lpeak, correlation
                        )
                        
                        if match_info is not None:
                            batch_matches.append(match_info)
                            
                    except Exception as e:
                        _LOG.warning(f"Error processing template {tpl.get('name', 'Unknown')} with legacy forced redshift: {e}")
                        continue

            # Add batch matches to total matches
            matches.extend(batch_matches)
            
            # Update progress counter
            processed_templates += len(batch_templates)
            
            # Performance info for this batch
            batch_time = time.time() - batch_start_time
            _LOG.info(f"  ✓ Type {sn_type} batch {batch_idx}/{len(batches)}: {len(batch_matches)} matches found in {batch_time:.2f}s")

    # Calculate total time and performance metrics
    total_time = time.time() - start_time
    templates_per_second = len(templates) / total_time if total_time > 0 else 0
    
    _LOG.info(f"🎯 OPTIMIZED forced redshift analysis completed: {len(matches)} matches found (z={forced_redshift:.6f})")
    _LOG.info(f"⚡ Performance: {total_time:.2f}s total, {templates_per_second:.1f} templates/sec")
    _LOG.info(f"⚡ Average: {total_time/len(templates)*1000:.1f}ms per template")
    
    # Sort matches by rlap (descending) to get best matches first
    matches.sort(key=lambda x: x['rlap'], reverse=True)
    
    return matches


def _process_forced_redshift_match(
    tpl: Dict[str, Any],
    tpl_shifted: np.ndarray,
    tapered_flux: np.ndarray,
    log_wave: np.ndarray,
    cont: np.ndarray,
    forced_redshift: float,
    forced_lag: float,
    dtft: np.ndarray,
    drms: float,
    NW_grid: int,
    DWLOG_grid: float,
    k1: int, k2: int, k3: int, k4: int,
    lapmin: float,
    rlapmin: float,
    left_edge: int,
    right_edge: int,
    lap: float,
    lpeak: float,
    correlation: Optional[np.ndarray] = None
) -> Optional[Dict[str, Any]]:
    """
    Process a single forced redshift match with optimized correlation handling.
    
    This function handles the detailed correlation analysis for a template at the forced redshift,
    calculating all necessary metrics and quality indicators.
    """
    from .fft_tools import calculate_rms, aspart, apply_filter as bandpass
    from .preprocessing import apodize, pad_to_NW
    
    try:
        # Trim both arrays to overlapping region and prepare for FFT
        (t0, t1), (d0, d1), (ov_start, ov_end), _ = overlap(tpl_shifted, tapered_flux, log_wave)
        
        start_trim = max(t0, d0)
        end_trim = min(t1, d1)
        
        if end_trim <= start_trim:
            return None
        
        work_d = tapered_flux[start_trim:end_trim + 1].copy()
        work_t = tpl_shifted[start_trim:end_trim + 1].copy()
        
        if len(work_d) == 0 or len(work_t) == 0:
            return None
        
        # Apodize the trimmed regions
        apodize_percent = 10.0
        work_d = apodize(work_d, 0, len(work_d) - 1, percent=apodize_percent)
        work_t = apodize(work_t, 0, len(work_t) - 1, percent=apodize_percent)
        
        # Pad to NW
        work_d = pad_to_NW(work_d, NW_grid)
        work_t = pad_to_NW(work_t, NW_grid)
        
        # Calculate new FFTs and RMS values
        dtft_peak = np.fft.fft(work_d)
        ttft_peak = np.fft.fft(work_t)
        
        drms_peak = calculate_rms(dtft_peak, k1, k2, k3, k4)
        trms_peak = calculate_rms(ttft_peak, k1, k2, k3, k4)
        
        if drms_peak == 0 or trms_peak == 0:
            return None

        # Calculate correlation on trimmed spectra
        cross_power_peak = dtft_peak * np.conj(ttft_peak)
        cspec_filtered_peak = bandpass(cross_power_peak, k1, k2, k3, k4)
        ccf_peak = np.fft.ifft(cspec_filtered_peak).real
        Rz_peak = np.roll(ccf_peak, NW_grid//2)
        if drms_peak * trms_peak > 0:
            Rz_peak /= (NW_grid * drms_peak * trms_peak)

        # For forced redshift, the peak should be at the zero-lag position (center)
        mid = NW_grid // 2
        peak_idx = mid  # Force peak to be at center since we forced the redshift
        hgt_p = Rz_peak[peak_idx]
        
        # For forced redshift mode, we don't need peak fitting - use direct values
        z_est = forced_redshift
        
        # Calculate width for uncertainty estimation
        width = 0.0
        z_width = 0.0
        
        # Half-maximum width estimate
        try:
            half_max = hgt_p * 0.5
            if half_max > 0:
                left_idx = peak_idx
                right_idx = peak_idx
                
                # Search left and right
                for i in range(peak_idx - 1, max(0, peak_idx - 10), -1):
                    if Rz_peak[i] <= half_max:
                        left_idx = i
                        break
                for i in range(peak_idx + 1, min(NW_grid, peak_idx + 10)):
                    if Rz_peak[i] <= half_max:
                        right_idx = i
                        break
                
                if right_idx > left_idx:
                    fwhm_pixels = float(right_idx - left_idx)
                    width = fwhm_pixels / 2.35
                    z_width = np.exp(width * DWLOG_grid) - 1.0
        except:
            pass
        
        # Conservative fallback estimate
        if width == 0.0:
            width = 2.0
            z_width = np.exp(width * DWLOG_grid) - 1.0
        
        # Calculate R value and final rlap
        arms_raw, _ = aspart(cross_power_peak, k1, k2, k3, k4, 0)
        arms_norm = arms_raw / (NW_grid * drms_peak * trms_peak)

        if arms_norm > 0:
            r_value = hgt_p / (2 * arms_norm)
        else:
            r_value = 0.0

        rlap = r_value * lpeak

        # Store results if they pass quality criteria
        if rlap >= rlapmin and lap >= lapmin:
            # Calculate formal redshift error using canonical SNID formula
            zk = 3.0/8.0
            if z_width > 0 and r_value > 0:
                formal_z_error = zk * z_width / (1.0 + r_value)
            else:
                formal_z_error = z_width if z_width > 0 else 0.0
            
            # Create match dictionary
            match_info = {
                "template": tpl,
                "name": tpl["name"],
                "type": tpl.get("type", "Unknown"),
                "subtype": tpl.get("subtype", ""),
                "age": tpl.get("age", 0.0),
                "redshift": z_est,
                "redshift_error": formal_z_error,
                "r": r_value,
                "lap": lap,
                "rlap": rlap,
                "peak_height": hgt_p,
                "peak_width": width,
                "processed_flux": tpl_shifted[left_edge:right_edge+1],
                "correlation": {
                    "z_axis_full": np.array([forced_redshift]),
                    "correlation_full": np.array([hgt_p]),
                    "z_axis_peak": np.array([forced_redshift]),
                    "correlation_peak": np.array([hgt_p]),
                    "initial_lag": forced_lag,
                    "final_lag": forced_lag,
                    "dtft": dtft_peak,
                    "ttft": ttft_peak,
                    "drms2": drms_peak,
                    "trms2": trms_peak,
                    "cross_power": cross_power_peak,
                    "cspec_filtered": cspec_filtered_peak
                },
                "spectra": {
                    "flat": {
                        "wave": log_wave[left_edge:right_edge+1],
                        "flux": tpl_shifted[left_edge:right_edge+1]
                    },
                    "flux": {
                        "wave": log_wave[left_edge:right_edge+1],
                        "flux": (tpl_shifted[left_edge:right_edge+1] + 1.0) * cont[left_edge:right_edge+1]
                    }
                },
                "forced_redshift": True  # Flag to indicate this was forced
            }
            
            return match_info
        
        return None
        
    except Exception as e:
        _LOG.warning(f"Error in _process_forced_redshift_match for template {tpl.get('name', 'Unknown')}: {e}")
        return None


def run_snid_analysis(
    processed_spectrum: Dict[str, np.ndarray],
    templates_dir: str,
    *,
    # Analysis parameters
    zmin: float = -0.01,
    zmax: float = 1.0,
    age_range: Optional[Tuple[float, float]] = None,
    type_filter: Optional[List[str]] = None,
    template_filter: Optional[List[str]] = None,
    exclude_templates: Optional[List[str]] = None,
    peak_window_size: int = 10,
    lapmin: float = 0.3,
    rlapmin: float = 4,
    rlap_ccc_threshold: float = 1.8,  # NEW: RLAP-CCC threshold for clustering
    # NEW: Forced redshift parameter
    forced_redshift: Optional[float] = None,
    # Output options
    max_output_templates: int = 5,
    verbose: bool = False,
    # Performance options
    # Plotting options
    show_plots: bool = True,
    save_plots: bool = False,
    plot_dir: Optional[str | Path] = None,
    # Progress callback
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Tuple[SNIDResult, Dict[str, Any]]:
    """
    Run SNID correlation analysis on preprocessed spectrum.
    
    This function takes a preprocessed spectrum (from preprocess_spectrum) and
    performs template matching, type determination, and statistical analysis.
    
    Parameters
    ----------
    processed_spectrum : dict
        Preprocessed spectrum from preprocess_spectrum() function
    templates_dir : str
        Path to directory containing template spectra
    zmin, zmax : float
        Redshift range for analysis
    age_range : tuple of (float, float), optional
        Age range in days to consider for templates
    type_filter : list of str, optional
        Only use templates of these types
    template_filter : list of str, optional
        Only use templates with these specific names
    exclude_templates : list of str, optional
        Templates to exclude from analysis
    peak_window_size : int
        Window size for finding correlation peaks
    lapmin : float
        Minimum overlap fraction required
    rlapmin : float
        Minimum rlap value required for a match
    forced_redshift : float, optional
        If provided, bypass redshift search and force all templates to this redshift.
        When set, all templates will be shifted to this exact redshift value,
        skipping the initial correlation-based redshift determination.
    max_output_templates : int
        Maximum number of best templates to include in results
    verbose : bool
        Whether to print detailed information
    show_plots : bool
        Whether to display plots
    save_plots : bool
        Whether to save plots to files
    plot_dir : str or Path, optional
        Directory for saving plots
    progress_callback : callable, optional
        Callback function to report progress
        
    Returns
    -------
    result : SNIDResult
        Object containing all results and matches
    analysis_trace : dict
        Dictionary with diagnostic information from analysis
    """
    
    tic = time.time()
    analysis_trace = {}
    
    # Helper function for progress reporting
    def report_progress(message, progress=None):
        if progress_callback:
            try:
                progress_callback(message, progress)
            except Exception:
                pass  # Don't let progress reporting break the analysis
    
    _LOG.info("="*60)
    _LOG.info("SNID CORRELATION ANALYSIS")
    _LOG.info("="*60)
    report_progress("Starting SNID correlation analysis")
    
    # Extract preprocessed data with validation
    try:
        log_wave = processed_spectrum['log_wave']
        tapered_flux = processed_spectrum['tapered_flux']
        flat_flux = processed_spectrum['flat_flux']
        cont = processed_spectrum['continuum']
        left_edge = processed_spectrum['left_edge']
        right_edge = processed_spectrum['right_edge']
        grid_params = processed_spectrum['grid_params']
        
        # Validate that tapered_flux is properly processed
        if tapered_flux is None:
            raise ValueError("tapered_flux is None - preprocessing may have failed")
        if len(tapered_flux) == 0:
            raise ValueError("tapered_flux is empty - preprocessing may have failed")
        if np.all(tapered_flux == 0):
            raise ValueError("tapered_flux is all zeros - apodization may have failed")
            
        _LOG.debug(f"Extracted preprocessed data: {len(tapered_flux)} points in tapered_flux")
        
    except KeyError as e:
        raise ValueError(f"Missing required key in processed_spectrum: {e}. "
                        f"Available keys: {list(processed_spectrum.keys())}") from e
    except Exception as e:
        raise ValueError(f"Error extracting preprocessed data: {e}") from e
    
    # Get grid parameters
    NW_grid = grid_params['NW']
    DWLOG_grid = grid_params['DWLOG']
    
    # Initialize result object
    result = SNIDResult(
        success=False,
        min_rlap=rlapmin,
        dwlog=DWLOG_grid
    )
    
    # Store input spectrum info
    result.input_spectrum = processed_spectrum['input_spectrum']
    result.log_wave = log_wave
    
    # Store processed versions without zero edges for plotting
    result.processed_spectrum = {
        'log_wave': log_wave[left_edge:right_edge+1],
        'log_flux': (tapered_flux[left_edge:right_edge+1] + 1.0) * cont[left_edge:right_edge+1],
        'flat_flux': tapered_flux[left_edge:right_edge+1],
        'continuum': cont[left_edge:right_edge+1]
    }
    
    # Store flattened input data for plotting (use apodized version)
    result.flat_input = {
        'wave': log_wave[left_edge:right_edge+1],
        'flux': tapered_flux[left_edge:right_edge+1]  # FIXED: Use apodized version
    }
    
    # Store input continuum for plotting functions
    result.input_continuum = {
        'wave': log_wave[left_edge:right_edge+1],
        'flux': cont[left_edge:right_edge+1]
    }

    # ============================================================================
    # STEP 7: LOAD TEMPLATES (ONLY FOR NON-FORCED ANALYSIS)
    # ============================================================================
    
    # Skip template loading for forced redshift analysis (new method handles its own loading)
    if forced_redshift is None:
        # NORMAL ANALYSIS: Load templates here
        # Start template loading phase (will drive overall progress from ~25% to 100%)
        report_progress("Loading template library", 25)
        
        # Use unified storage for loading templates
        try:
            # Wire progress through to GUI: template loading will report incremental percentages
            # Scale template-loading progress to fit within overall analysis range (~50–75%)
            templates = load_templates_unified(
                templates_dir,
                type_filter=type_filter,
                template_names=template_filter,
                exclude_templates=exclude_templates,
                progress_callback=lambda msg, pct: report_progress(
                    f"{msg}",
                    25 + (0.75 * float(pct or 0.0))
                )
            )
            _LOG.info(f"✅ Loaded {len(templates)} templates using UNIFIED STORAGE")
        except Exception as e:
            _LOG.warning(f"Unified storage failed, falling back to legacy loader: {e}")
            templates, _ = load_templates(templates_dir, flatten=True)
            
            # Apply template filtering to legacy templates
            if template_filter:
                templates = [t for t in templates if t.get('name', '') in template_filter]
                _LOG.info(f"Applied template filter: {len(templates)} templates remaining")
            elif exclude_templates:
                original_count = len(templates)
                templates = [t for t in templates if t.get('name', '') not in exclude_templates]
                _LOG.info(f"Excluded {original_count - len(templates)} templates: {len(templates)} remaining")
            
            _LOG.info(f"✅ Loaded {len(templates)} templates using STANDARD method")
        
        if not templates:
            _LOG.error("No templates loaded")
            result.success = False
            return result, analysis_trace

        # ============================================================================
        # STEP 7a: OPTIONAL FILTERING BY AGE AND TYPE
        # ============================================================================
        # Default behavior: exclude Galaxy templates from full analysis unless explicitly requested
        if not type_filter:
            pre_count = len(templates)
            templates = [
                t for t in templates
                if (str(t.get('type', '')) not in ('Galaxy', 'Gal') and
                    not str(t.get('type', '')).startswith('Gal-'))
            ]
            if len(templates) < pre_count:
                _LOG.info(f"Step 7a: Default exclusion of Galaxy templates: {pre_count} -> {len(templates)}")

        original_count = len(templates)
        
        if age_range is not None:
            report_progress(f"Filtering templates by age range: {age_range}")
            age_min, age_max = age_range
            templates = [t for t in templates if age_min <= t.get('age', 0) <= age_max]
            _LOG.info(f"Step 7a: Age filtering: {original_count} -> {len(templates)} templates")
        
        if type_filter is not None and len(type_filter) > 0:
            report_progress(f"Filtering templates by type: {type_filter}")
            templates = [t for t in templates if t.get('type', '') in type_filter]
            _LOG.info(f"Step 7a: Type filtering: {original_count} -> {len(templates)} templates")
        
        if len(templates) == 0:
            report_progress("No templates remaining after filtering")
            _LOG.error("ERROR: No templates remaining after filtering")
            result.success = False
            return result, analysis_trace
    else:
        # FORCED REDSHIFT ANALYSIS: Templates will be loaded by the analysis function
        _LOG.info("⏭️  Skipping template loading - forced redshift analysis will handle loading by type")
        templates = []  # Placeholder for consistency

    # ============================================================================
    # STEP 8: PREPARE K-GRID & HELPERS
    # ============================================================================
    k1, k2 = 1, 4
    k3, k4 = NW_grid//12, NW_grid//10
    _LOG.debug(f"Step 8: Frequency band limits k1,k2,k3,k4 = {k1},{k2},{k3},{k4}")

    # Calculate the bin offsets needed to cover the full redshift range
    mid = NW_grid // 2
    lz1 = int(round(np.log(1 + zmin) / DWLOG_grid)) + mid
    lz2 = int(round(np.log(1 + zmax) / DWLOG_grid)) + mid

    # Ensure we have enough bins to cover the full redshift range
    if lz2 >= NW_grid:
        # _LOG.warning(f"High redshift {zmax} requires {lz2-mid} bins, but only {NW_grid-mid} available")
        lz2 = NW_grid - 1
    if lz1 < 0:
        # _LOG.warning(f"Low redshift {zmin} requires {lz1-mid} bins, but minimum is {-mid}")
        lz1 = 0

    # Compute redshift values for logging. Always compute to avoid referencing
    # undefined variables when formatting the debug string.
    z_lz1 = np.exp((lz1 - mid) * DWLOG_grid) - 1
    z_lz2 = np.exp((lz2 - mid) * DWLOG_grid) - 1
    _LOG.debug(
        f"Step 8: Redshift bin range: {lz1 - mid} to {lz2 - mid} (z = {z_lz1:.6f} to {z_lz2:.6f})"
    )

    # ============================================================================
    # STEP 9: PREPARE SPECTRUM FFT FOR CORRELATION
    # ============================================================================
    report_progress("Preparing spectrum for correlation analysis")
    dtft, drms = dtft_drms(tapered_flux, 0.0, left_edge, right_edge, k1, k2, k3, k4)
    
    _LOG.info(f"Step 9: Prepared data FFT (drms = {drms:.6f})")
    
    # ============================================================================
    # PHASE 1: CORRELATION ANALYSIS (OR FORCED REDSHIFT ANALYSIS)
    # ============================================================================
    
    # Check if forced redshift mode is enabled
    if forced_redshift is not None:
        # FORCED REDSHIFT MODE: Bypass normal correlation search
        report_progress(f"Starting forced redshift analysis (z={forced_redshift:.6f})")
        _LOG.info(f"Phase 1: FORCED REDSHIFT analysis z={forced_redshift:.6f}")
        _LOG.info("  → Skipping normal correlation search, using per-type template loading")
        
        # Additional debugging for forced redshift + advanced preprocessing
        _LOG.debug(f"Forced redshift analysis parameters:")
        _LOG.debug(f"  - tapered_flux shape: {tapered_flux.shape}")
        _LOG.debug(f"  - tapered_flux range: {np.min(tapered_flux):.2e} to {np.max(tapered_flux):.2e}")
        _LOG.debug(f"  - log_wave shape: {log_wave.shape}")
        _LOG.debug(f"  - left_edge: {left_edge}, right_edge: {right_edge}")
        _LOG.debug(f"  - NW_grid: {NW_grid}, DWLOG_grid: {DWLOG_grid}")
        
        try:
            matches = _run_forced_redshift_analysis_optimized(
                templates_dir, type_filter, template_filter, exclude_templates, age_range,
                tapered_flux, dtft, drms, left_edge, right_edge, 
                forced_redshift, NW_grid, DWLOG_grid, k1, k2, k3, k4, 
                lapmin, rlapmin, zmin, zmax, log_wave, cont, report_progress
            )
            
            _LOG.info(f"Phase 1 complete: Forced redshift analysis found {len(matches)} matches with rlap >= {rlapmin}")
            
        except Exception as e:
            _LOG.error(f"Error in forced redshift analysis: {e}")
            _LOG.error(f"This may be due to incompatible preprocessing data structure")
            import traceback
            _LOG.debug(f"Forced redshift analysis traceback: {traceback.format_exc()}")
            raise
        
    else:
        # NORMAL CORRELATION MODE: Full redshift search
        report_progress(f"Starting correlation analysis for {len(templates)} templates")
        _LOG.info(f"Phase 1: Processing {len(templates)} templates for correlation analysis...")
        _LOG.info(f"  → Searching redshift range {zmin:.6f} to {zmax:.6f}")
        
        matches = []
        
        # ============================================================================
        # OPTIMIZED VECTORIZED TEMPLATE CORRELATION
        # ============================================================================
        
        # Check if vectorized FFT optimization is available and enabled
        use_vectorized = True  # Default to optimized method
        
        # Try to detect if unified storage is being used (indicates optimization is available)
        try:
            # Check if we can use the optimization system
            from .core.integration import integrate_fft_optimization
            from .core.config import SNIDConfig
            
            # Create a configuration object for optimization settings
            config = SNIDConfig(use_vectorized_fft=use_vectorized)
            optimization_available = True
            
        except ImportError:
            optimization_available = False
            use_vectorized = False
        
        if optimization_available and use_vectorized and len(templates) > 10:
            # ============================================================================
            # VECTORIZED FFT CORRELATION BY TYPE (6.6x FASTER + TYPE PROGRESS)
            # ============================================================================
            _LOG.info(f"🚀 Using optimized vectorized FFT correlation by type for {len(templates)} templates")
            
            # Track performance for comparison
            vectorized_start_time = time.time()
            
            try:
                # Group templates by type for better progress reporting and GitHub file size
                templates_by_type = {}
                for template in templates:
                    sn_type = template.get('type', 'Unknown')
                    if sn_type not in templates_by_type:
                        templates_by_type[sn_type] = []
                    templates_by_type[sn_type].append(template)
                
                _LOG.info(f"🔄 Processing {len(templates_by_type)} supernova types: {list(templates_by_type.keys())}")
                
                # Calculate total templates and track progress
                total_templates = len(templates)
                processed_templates = 0
                
                # ------------------------------------------------------------------
                # Create processing order: Ia first, all II* second, then the rest
                # ------------------------------------------------------------------
                ordered_types: List[str] = []
                if 'Ia' in templates_by_type:
                    ordered_types.append('Ia')
                # Add any type that starts with "II" (e.g., II, II-P, IIb ...)
                ordered_types.extend([t for t in templates_by_type.keys() if t.startswith('II') and t not in ordered_types])
                # Finally add the remaining types preserving original insertion order
                ordered_types.extend([t for t in templates_by_type.keys() if t not in ordered_types])

                _LOG.info(f"🔄 Processing order: {ordered_types}")

                # ------------------------------------------------------------------
                # Process each type sequentially (optionally batched for large types)
                # ------------------------------------------------------------------
                for type_idx, sn_type in enumerate(ordered_types):
                    type_templates = templates_by_type[sn_type]

                    # ------------------------------------------------------------------
                    # Decide batching strategy
                    # ------------------------------------------------------------------
                    batch_parts = 1
                    if sn_type == 'Ia':
                        batch_parts = 4  # Split Type Ia into 4 batches
                    elif sn_type.startswith('II'):
                        batch_parts = 2  # Split all Type II* into 2 batches

                    if batch_parts > 1:
                        batch_size = math.ceil(len(type_templates) / batch_parts)
                        batches = [type_templates[i:i + batch_size] for i in range(0, len(type_templates), batch_size)]
                    else:
                        batches = [type_templates]

                    _LOG.info(f"🔄 Type {sn_type}: {len(type_templates)} templates split into {len(batches)} batch(es)")

                    # --------------------------------------------------------------
                    # Process each batch
                    # --------------------------------------------------------------
                    for batch_idx, batch_templates in enumerate(batches, start=1):
                        # Quiet progress update BEFORE heavy computation (no text, just bar)
                        batch_start_progress = (processed_templates / total_templates) * 100
                        report_progress("", batch_start_progress)

                        # Track time for this batch (useful for debugging/perf)
                        batch_start_time = time.time()

                        # ------------------------------------------------------
                        # Correlation for this batch
                        # ------------------------------------------------------
                        correlator = integrate_fft_optimization(batch_templates, k1, k2, k3, k4, config=config)
                        correlation_results = correlator.correlate_snid_style(dtft, drms)

                        # Vectorized peak finding and match processing (same as before)
                        type_matches = 0

                        try:
                            from .vectorized_peak_finder import VectorizedPeakFinder
                            peak_finder = VectorizedPeakFinder(NW_grid, DWLOG_grid, lz1, lz2, k1, k2, k3, k4)

                            correlation_matrix = []
                            template_names = []
                            template_rms_array = []
                            template_data_dict = {}

                            for template_name, corr_result in correlation_results.items():
                                correlation = corr_result['correlation']
                                template_data = corr_result['template']
                                template_rms = corr_result['template_rms']
                                if drms > 0 and template_rms > 0:
                                    correlation_matrix.append(correlation)
                                    template_names.append(template_name)
                                    template_rms_array.append(template_rms)
                                    template_data_dict[template_name] = template_data.metadata

                            if correlation_matrix:
                                correlation_matrix = np.array(correlation_matrix)
                                template_rms_array = np.array(template_rms_array)
                                peak_results = peak_finder.find_peaks_batch(correlation_matrix, template_names, template_rms_array, drms)

                                for template_name, peak_data in peak_results.items():
                                    correlation = peak_data['correlation']
                                    peaks = peak_data['peaks']
                                    template_meta = template_data_dict[template_name]
                                    template_rms = peak_data['template_rms']
                                    template_flux = template_meta.get('flux', np.array([]))
                                    if len(template_flux) == 0:
                                        continue
                                    template_matches = _process_template_peaks(
                                        peaks.tolist(), correlation, template_flux, template_meta,
                                        tapered_flux, log_wave, NW_grid, DWLOG_grid, k1, k2, k3, k4,
                                        lapmin, rlapmin, zmin, zmax, peak_window_size, cont, left_edge, right_edge,
                                        template_fft=correlation_results[template_name]['template_fft'], template_rms=template_rms
                                    )
                                    matches.extend(template_matches)
                                    type_matches += len(template_matches)

                        except Exception as e:
                            # Fallback to existing per-template processing if vectorized peak finder not available
                            _LOG.debug(f"Peak finder fallback: {e}")
                            for template_name, corr_result in correlation_results.items():
                                correlation = corr_result['correlation']
                                template_data = corr_result['template']
                                template_meta = template_data.metadata
                                template_rms = corr_result['template_rms']
                                if drms > 0 and template_rms > 0:
                                    Rz_rolled = np.roll(correlation, NW_grid // 2)
                                    Rz = Rz_rolled / (NW_grid * drms * template_rms)
                                else:
                                    continue
                                peaks_indices, _ = find_peaks(Rz, distance=3, height=0.3)
                                valid_peaks_indices = [i for i in peaks_indices if lz1 <= i <= lz2]
                                if not valid_peaks_indices:
                                    continue
                                template_matches = _process_template_peaks(
                                    valid_peaks_indices, Rz, template_data.flux, template_meta, tapered_flux, log_wave,
                                    NW_grid, DWLOG_grid, k1, k2, k3, k4, lapmin, rlapmin, zmin, zmax, peak_window_size,
                                    cont, left_edge, right_edge, template_fft=corr_result['template_fft'], template_rms=template_rms)
                                matches.extend(template_matches)
                                type_matches += len(template_matches)

                        # Update processed count & progress AFTER batch
                        processed_templates += len(batch_templates)
                        batch_duration = time.time() - batch_start_time
                        final_progress = (processed_templates / total_templates) * 100

                        # Skip empty progress update - we don't want empty lines in the UI

                        _LOG.info(f"✅ Type {sn_type} batch {batch_idx}/{len(batches)} complete ({len(batch_templates)} templates, {batch_duration:.2f}s)")

                    # End of batch loop
                    # Final summary progress update for this type
                    report_progress(f"✅ {sn_type} processed", (processed_templates / total_templates) * 100)
                    _LOG.info(f"✅ Type {sn_type} fully processed ({len(type_templates)} templates)")
                # End of type loop

                # Calculate total vectorized time
                vectorized_total_time = time.time() - vectorized_start_time
                templates_per_second = len(templates) / vectorized_total_time if vectorized_total_time > 0 else 0
                
                _LOG.info(f"🚀 Vectorized type-by-type correlation analysis found {len(matches)} total matches")
                _LOG.info(f"⚡ Performance: {vectorized_total_time:.2f}s total, {templates_per_second:.1f} templates/sec")
                _LOG.info(f"⚡ Average: {vectorized_total_time/len(templates)*1000:.1f}ms per template")
                
                # Report final completion
                report_progress(f"✅ Correlation complete: {len(matches)} matches found", 100)
                
            except Exception as e:
                _LOG.warning(f"Vectorized FFT correlation failed: {e}")
                _LOG.warning("Falling back to legacy template-by-template method")
                use_vectorized = False
        else:
            use_vectorized = False
            
        if not use_vectorized:
            # ============================================================================
            # LEGACY TEMPLATE-BY-TEMPLATE CORRELATION (FALLBACK)
            # ============================================================================
            _LOG.info(f"⚙️  Using legacy template-by-template correlation for {len(templates)} templates")
            
            # Track performance for comparison
            legacy_start_time = time.time()
            
            # Progress tracking for templates
            total_templates = len(templates)
            template_progress_interval = 500  # Report every 500 templates instead of percentage-based
            
            for template_idx, tpl in enumerate(templates):
                # Report progress every 500 templates or at the end
                if template_idx % template_progress_interval == 0 or template_idx == total_templates - 1:
                    progress_pct = (template_idx + 1) / total_templates * 100
                    # Check if using optimized templates
                    method_name = "⚡ OPTIMIZED" if tpl.get('is_log_rebinned', False) else "🐌 legacy method"
                    report_progress(f"{method_name} Template {template_idx + 1}/{total_templates}", progress_pct)
                    _LOG.debug(f"  Template {template_idx + 1}/{total_templates}")
                
                # Get template flux (ensuring it's not None and has correct size)
                tplate = tpl.get('flux', None)
                if tplate is None or len(tplate) != NW_grid:
                    continue
                
                # OPTIMIZED: Use pre-computed FFT if available (skips rebinning and FFT calculation)
                if tpl.get('is_log_rebinned', False) and 'pre_computed_fft' in tpl:
                    # Template is already rebinned to standard grid, use pre-computed FFT
                    ttft = tpl['pre_computed_fft']
                    trms = calculate_rms(ttft, k1, k2, k3, k4)
                    _LOG.debug(f"Using pre-computed FFT for template {tpl.get('name', 'unknown')} (FAST PATH)")
                else:
                    # Legacy path: compute FFT at runtime (slower)
                    ttft, trms = dtft_drms(tplate, 0.0, 0, NW_grid-1, k1, k2, k3, k4)
                    if template_idx < 5:  # Only log first few times
                        _LOG.debug(f"Computing FFT at runtime for template {tpl.get('name', 'unknown')} (SLOW PATH)")
                
                if drms <= 0 or trms <= 0:
                    continue

                # First correlation (pre-trimming)
                cross_power_unscaled = dtft * np.conj(ttft)
                cspec_filtered_unscaled = bandpass(cross_power_unscaled, k1, k2, k3, k4)
                ccf = np.fft.ifft(cspec_filtered_unscaled).real
                Rz_rolled = np.roll(ccf, NW_grid//2)
                Rz = Rz_rolled / (NW_grid * drms * trms) if (drms * trms) != 0 else Rz_rolled
            
                # Find peaks in allowed redshift range
                peaks_indices, properties = find_peaks(Rz, distance=3, prominence=0.1, height=0.1)
                valid_peaks_indices = [i for i in peaks_indices if lz1 <= i <= lz2]

                if not valid_peaks_indices:
                    continue

                # Process each peak using the extracted helper function
                template_matches = _process_template_peaks(
                    valid_peaks_indices, Rz, tplate, tpl, tapered_flux, log_wave,
                    NW_grid, DWLOG_grid, k1, k2, k3, k4, lapmin, rlapmin,
                    zmin, zmax, peak_window_size, cont, left_edge, right_edge
                )
                
                matches.extend(template_matches)
        
        # Performance summary for legacy method
        if not use_vectorized:
            legacy_total_time = time.time() - legacy_start_time
            templates_per_second = len(templates) / legacy_total_time if legacy_total_time > 0 else 0
            _LOG.info(f"⚙️  Legacy correlation complete: {len(matches)} matches found")
            _LOG.info(f"⏱️  Performance: {legacy_total_time:.2f}s total, {templates_per_second:.1f} templates/sec")
            _LOG.info(f"⏱️  Average: {legacy_total_time/len(templates)*1000:.1f}ms per template")
        
        _LOG.info(f"Phase 1 complete: Normal correlation analysis found {len(matches)} matches with rlap >= {rlapmin}")

    # END of if/else block for forced_redshift vs normal analysis

    # ============================================================================
    # PHASE 2: PROCESS RESULTS AND COMPUTE STATISTICS
    # ============================================================================
    report_progress("Processing results and computing statistics")
    _LOG.info("Phase 2: Processing results and computing statistics...")

    # ============================================================================
    # COMPUTE RLAP-CCC METRIC FOR ENHANCED GMM CLUSTERING
    # ============================================================================
    
    # Compute RLAP-CCC metric before clustering (multiply RLAP with capped CCC similarity)
    # Always compute when we have any matches so weak/single-match cases still use RLAP-CCC
    if len(matches) >= 1:
        # Check if RLAP-CCC is already computed for all matches
        already_computed = all('rlap_ccc' in match for match in matches)
        
        if already_computed:
            _LOG.info("RLAP-CCC metric already computed for all matches - skipping computation")
        else:
            try:
                from snid_sage.shared.utils.math_utils import compute_rlap_ccc_metric
                report_progress("Computing RLAP-CCC similarity metrics")
                _LOG.info("Computing RLAP-CCC metric for enhanced GMM clustering")
                
                # Pass the full processed spectrum for exact spectrum preparation matching snid_enhanced_metrics.py
                processed_spectrum_for_ccc = {
                    'tapered_flux': tapered_flux,
                    'display_flat': processed_spectrum.get('display_flat'),  # May be None, which is fine
                    'flat_flux': flat_flux, 
                    'left_edge': left_edge,
                    'right_edge': right_edge,
                    'log_wave': log_wave
                }
                
                # Enhance matches with RLAP-CCC metric using exact spectrum preparation
                matches = compute_rlap_ccc_metric(matches, processed_spectrum_for_ccc, verbose=verbose)
                
                _LOG.info(f"RLAP-CCC metric computed for {len(matches)} matches")
                
            except Exception as e:
                _LOG.warning(f"RLAP-CCC computation failed, using original RLAP: {e}")
                # Add dummy rlap_ccc field equal to original rlap for compatibility
                for match in matches:
                    match['rlap_ccc'] = match.get('rlap', 0.0)
                    match['original_rlap'] = match.get('rlap', 0.0)
                    match['ccc_similarity'] = 0.0
                    match['ccc_similarity_capped'] = 0.0

    # ============================================================================
    # IMPROVED TOP-10% RLAP-CCC GMM CLUSTERING (NOW DEFAULT)
    # ============================================================================
    
    clustering_results = None
    # Pre-compute RLAP-CCC thresholded list for fallback paths and summary logic
    try:
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        thresholded_matches = [m for m in matches if get_best_metric_value(m) >= float(rlap_ccc_threshold)]
    except Exception:
        thresholded_matches = list(matches)
    
    if len(matches) >= 1:  # Allow clustering with any number of matches
        try:
            from .cosmological_clustering import perform_direct_gmm_clustering
            
            report_progress("Performing cosmological GMM clustering analysis with best metric")
            _LOG.info("Using direct GMM clustering on redshift values with best available metric RLAP-CCC (fallback to RLAP when absent)")
            
            clustering_results = perform_direct_gmm_clustering(
                matches, 
                min_matches_per_type=1,  # Accept any type with at least 1 match
                quality_threshold=0.05,  # Fixed threshold in z space
                max_clusters_per_type=10,
                top_percentage=0.10,  # Top 10% of matches
                verbose=verbose,
                use_rlap_cos=True,  # NEW: Use RLAP-Cos instead of RLAP
                rlap_ccc_threshold=rlap_ccc_threshold  # NEW: RLAP-CCC threshold
            )
            
            if clustering_results['success'] and clustering_results['best_cluster']:
                filtered_matches = clustering_results['best_cluster']['matches']
                best_type = clustering_results['best_cluster']['type']
                top_5_mean = clustering_results['best_cluster'].get('top_5_mean', 0)
                
                _LOG.info(f"Cosmological GMM: {len(matches)} -> {len(filtered_matches)} matches")
                _LOG.info(f"Best cluster: {best_type} (top-5 mean: {top_5_mean:.2f})")
                
                # Store clustering results for plotting
                result.clustering_results = clustering_results
                result.clustering_method = 'cosmological_gmm'
            else:
                # Separate cases: no survivors vs weak survivors
                if len(thresholded_matches) == 0:
                    _LOG.info("No matches survived RLAP-CCC threshold; skipping clustering")
                else:
                    _LOG.info("Clustering not reliable; proceeding with weak matches without forming a cluster")
                # If nothing survives the RLAP-CCC threshold, treat as no matches
                # Otherwise, treat surviving matches as weak (no clusters)
                filtered_matches = thresholded_matches
                result.clustering_method = 'none'
                # Preserve the failure reason for summary/GUI messaging
                try:
                    result.clustering_failure_reason = clustering_results.get('reason')
                except Exception:
                    result.clustering_failure_reason = 'unknown'
                result.clustering_results = None
                
        except ImportError as e:
            _LOG.error(f"Could not import improved clustering (sklearn required): {e}")
            filtered_matches = thresholded_matches
            result.clustering_method = 'none'
            result.clustering_failure_reason = 'exception'
            result.clustering_results = None
        except Exception as e:
            _LOG.error(f"Top-10% RLAP clustering failed: {e}")
            filtered_matches = matches
            result.clustering_method = 'none'
            result.clustering_results = None
    else:
        filtered_matches = thresholded_matches
        result.clustering_method = 'none'
        result.clustering_failure_reason = 'insufficient_matches'
        result.clustering_results = None
        _LOG.info(f"Not enough matches for GMM clustering, using all {len(matches)} matches")

    result.filtered_matches = filtered_matches

    # Statistical analysis and type determination (same as original)
    result.initial_redshift = compute_initial_redshift(matches)

    # Only report type classification step when there are reliable matches to classify
    try:
        if filtered_matches and len(filtered_matches) > 0:
            report_progress("Determining supernova type classification")
    except Exception:
        pass
    _LOG.info("Running type determination analysis...")
    
    # Use cluster-aware subtype determination if clustering was successful
    if (hasattr(result, 'clustering_results') and result.clustering_results and 
        result.clustering_results.get('success') and result.clustering_results.get('best_cluster')):
        
        best_cluster = result.clustering_results['best_cluster']
        winning_type = best_cluster['type']
        winning_cluster_idx = best_cluster.get('cluster_id', 0)
        
        _LOG.info(f"Using cluster-aware type determination for winning {winning_type} cluster")
        
        # Get GMM responsibilities for cluster-aware subtype determination
        type_clustering_results = result.clustering_results.get('type_clustering_results', {})
        type_data = type_clustering_results.get(winning_type, {})
        
        # Extract weighted redshift from the best cluster
        weighted_redshift = best_cluster.get('enhanced_redshift', result.initial_redshift)
        weighted_uncertainty = best_cluster.get('weighted_redshift_uncertainty', 0.01)
        
        if 'gamma' in type_data:
            # Use new cluster-aware subtype determination
            from .cosmological_clustering import choose_subtype_weighted_voting
            
            # Get the type matches that were actually used for clustering (stored with gamma matrix)
            type_matches = type_data.get('type_matches', [m for m in matches if m['template'].get('type') == winning_type])
            gamma = type_data['gamma']
            
            best_subtype, subtype_confidence, margin_over_second, second_best_subtype = choose_subtype_weighted_voting(
                winning_type, winning_cluster_idx, type_matches, gamma
            )
            
            _LOG.info(f"Cluster-aware subtype determination: {best_subtype} "
                     f"(confidence: {subtype_confidence:.3f}, margin: {margin_over_second:.3f}, second: {second_best_subtype})")
            
            # Create type determination result with cluster-based metrics
            type_determination = {
                'success': True,
                'consensus_type': winning_type,
                'consensus_subtype': best_subtype,
                'subtype_confidence': subtype_confidence,
                'subtype_margin_over_second': margin_over_second,
                'second_best_subtype': second_best_subtype,
                'cluster_metrics': {
                    'cluster_quality': best_cluster.get('redshift_quality', 'loose'),
                    'top_5_mean': best_cluster.get('top_5_mean', 0.0),
                    'cluster_size': best_cluster.get('size', 0),
                    'redshift_span': best_cluster.get('redshift_span', 0.0),
                    'mean_rlap': best_cluster.get('mean_rlap', 0.0)
                },
                'statistics': {
                    'getzt': {
                        'z_hybrid': weighted_redshift,
                        'z_hybrid_uncertainty': weighted_uncertainty,
                        'age_enhanced': 0.0, 
                        'age_enhanced_uncertainty': 0.0
                    },
                    'fractions': {'type_fractions': {winning_type: 1.0}, 'subtype_fractions': {}},
                    'slopes': {'type_slopes': {}},
                    'security': {
                        'method': 'cosmological_gmm_clustering',
                        'bttemp': f"{winning_type}_cluster_{winning_cluster_idx}",
                        'bsttemp': best_subtype, 
                        'btfrac': winning_type,
                        'btslope': winning_type, 
                        'bstfrac': best_subtype, 
                        'bstslope': best_subtype,
                        'cluster_based': True
                    }
                }
            }
        else:
            # Fallback: basic cluster-based type determination without subtype
            _LOG.warning("No GMM responsibilities available, using basic cluster-based type determination")
            
            # Ensure weighted redshift variables are available for fallback case too
            if 'weighted_redshift' not in locals():
                weighted_redshift = best_cluster.get('enhanced_redshift', result.initial_redshift)
                weighted_uncertainty = best_cluster.get('weighted_redshift_uncertainty', 0.01)
            
            type_determination = {
                'success': True,
                'consensus_type': winning_type,
                'consensus_subtype': 'Unknown',
                'cluster_metrics': {
                    'cluster_quality': best_cluster.get('redshift_quality', 'loose'),
                    'top_5_mean': best_cluster.get('top_5_mean', 0.0),
                    'cluster_size': best_cluster.get('size', 0),
                    'redshift_span': best_cluster.get('redshift_span', 0.0),
                    'mean_rlap': best_cluster.get('mean_rlap', 0.0)
                },
                'statistics': {
                    'getzt': {
                        'z_hybrid': weighted_redshift,
                        'z_hybrid_uncertainty': weighted_uncertainty,
                        'age_enhanced': 0.0, 
                        'age_enhanced_uncertainty': 0.0
                    },
                    'fractions': {'type_fractions': {winning_type: 1.0}, 'subtype_fractions': {}},
                    'slopes': {'type_slopes': {}},
                    'security': {
                        'method': 'basic_cluster_analysis',
                        'bttemp': f"{winning_type}_cluster_{best_cluster.get('cluster_id', 0)}",
                        'bsttemp': 'Unknown',
                        'btfrac': winning_type,
                        'btslope': winning_type,
                        'cluster_based': True
                    }
                }
            }
    else:
        # No clustering results - use simple type determination based on best matches
        _LOG.info("No clustering results available, using simple type determination")
        
        if filtered_matches:
            # Find most common type among filtered matches
            type_counts = {}
            type_rlaps = {}  # Track RLAP-cos values for each type
            for match in filtered_matches:
                tp = match['template'].get('type', 'Unknown')
                type_counts[tp] = type_counts.get(tp, 0) + 1
                if tp not in type_rlaps:
                    type_rlaps[tp] = []
                # Use RLAP-cos if available, otherwise RLAP
                from snid_sage.shared.utils.math_utils import get_best_metric_value
                type_rlaps[tp].append(get_best_metric_value(match))
            
            if type_counts:
                consensus_type = max(type_counts.items(), key=lambda x: x[1])[0]
                
                # Match quality and quantity metrics
                type_match_count = type_counts[consensus_type]
                max_rlap = max(type_rlaps[consensus_type]) if type_rlaps[consensus_type] else 0
                mean_rlap = sum(type_rlaps[consensus_type]) / len(type_rlaps[consensus_type]) if type_rlaps[consensus_type] else 0
            else:
                consensus_type = 'Unknown'
            
            # Use proper statistical redshift calculations instead of simple mean
            redshifts = [m['redshift'] for m in filtered_matches]
            if redshifts:
                from snid_sage.shared.utils.math_utils import calculate_weighted_redshift
                # Use RLAP values as weights (assuming filtered_matches has rlap values)
                weights = [m.get('rlap', 1.0) for m in filtered_matches]
                weighted_redshift, weighted_uncertainty = calculate_weighted_redshift(
                    redshifts, weights
                )
            else:
                weighted_redshift = result.initial_redshift
                weighted_uncertainty = 0.0
            
            type_determination = {
                'success': True,
                'consensus_type': consensus_type,
                'consensus_subtype': 'Unknown',  # No subtype without clustering
                'match_metrics': {
                    'type_match_count': type_counts.get(consensus_type, 0),
                    'max_rlap': max(type_rlaps.get(consensus_type, [0])),
                    'mean_rlap': sum(type_rlaps.get(consensus_type, [0])) / max(len(type_rlaps.get(consensus_type, [0])), 1),
                    'total_matches': len(filtered_matches)
                },
                'statistics': {
                    'getzt': {
                        'z_hybrid': weighted_redshift,
                        'z_hybrid_uncertainty': weighted_uncertainty,
                        'age_enhanced': 0.0, 
                        'age_enhanced_uncertainty': 0.0
                    },
                    'fractions': {'type_fractions': {consensus_type: 1.0}, 'subtype_fractions': {}},
                    'slopes': {'type_slopes': {}},
                    'security': {
                        'method': 'simple_vote_counting',
                        'bttemp': f"vote_winner_{consensus_type}",
                        'bsttemp': 'Unknown',
                        'btfrac': consensus_type,
                        'btslope': consensus_type,
                        'cluster_based': False
                    }
                }
            }
        else:
            # No matches at all
            type_determination = {
                'success': False,
                'consensus_type': 'Unknown',
                'consensus_subtype': 'Unknown',
                'match_metrics': {
                    'type_match_count': 0,
                    'max_rlap': 0.0,
                    'mean_rlap': 0.0,
                    'total_matches': 0
                },
                'statistics': {
                    'getzt': {
                        'z_mean': result.initial_redshift, 
                        'z_std': 0.0, 
                        'z_median': result.initial_redshift,
                        'age_mean': 0.0, 
                        'age_std': 0.0
                    },
                    'fractions': {'type_fractions': {}, 'subtype_fractions': {}},
                    'slopes': {'type_slopes': {}},
                    'security': {
                        'method': 'no_matches',
                        'bttemp': 'none',
                        'bsttemp': 'Unknown',
                        'btfrac': 'Unknown',
                        'btslope': 'Unknown',
                        'cluster_based': False
                    }
                }
            }

    if type_determination['success'] and filtered_matches:
        # Handle new cluster-aware statistics structure
        stats = type_determination.get('statistics', {})
        
        # Extract redshift information (with fallbacks for cluster-aware method)
        getzt_stats = stats.get('getzt', {})
        # Prefer the cluster-derived hybrid redshift when available
        if 'z_hybrid' in getzt_stats:
            result.consensus_redshift = getzt_stats['z_hybrid']
        else:
            result.consensus_redshift = getzt_stats.get('z_mean', result.initial_redshift)
        
        # Special handling for forced redshift mode where z_std would be zero
        if forced_redshift is not None:
            # In forced mode, use average of individual redshift errors instead of z_std
            individual_errors = [m.get('redshift_error', 0.0) for m in filtered_matches]
            if individual_errors and any(err > 0 for err in individual_errors):
                result.consensus_redshift_error = np.mean([err for err in individual_errors if err > 0])
            else:
                result.consensus_redshift_error = 0.0
        else:
            if 'z_hybrid_uncertainty' in getzt_stats:
                result.consensus_redshift_error = getzt_stats['z_hybrid_uncertainty']
            else:
                result.consensus_redshift_error = getzt_stats.get('z_std', 0.01)
        result.consensus_z_median = getzt_stats.get('z_median', result.initial_redshift)
        result.consensus_age = getzt_stats.get('age_enhanced', 0.0)
        result.consensus_age_error = getzt_stats.get('age_std', 0.0)
        
        result.consensus_type = type_determination['consensus_type']
        result.best_subtype = type_determination['consensus_subtype']
        

        
        # Store subtype confidence if available (from cluster-aware method)
        if 'subtype_confidence' in type_determination:
            result.subtype_confidence = type_determination['subtype_confidence']
        else:
            result.subtype_confidence = 0.0
        
        # Store new subtype margin information if available
        if 'subtype_margin_over_second' in type_determination:
            result.subtype_margin_over_second = type_determination['subtype_margin_over_second']
        else:
            result.subtype_margin_over_second = 0.0
            
        if 'second_best_subtype' in type_determination:
            result.second_best_subtype = type_determination['second_best_subtype']
        else:
            result.second_best_subtype = None
        
        # Handle type fractions and statistics with fallbacks
        frac_stats = stats.get('fractions', {})
        slope_stats = stats.get('slopes', {})
        security_stats = stats.get('security', {})
        
        result.type_fractions = frac_stats.get('type_fractions', {result.consensus_type: 1.0})
        result.type_fractions_weighted = compute_type_fractions(filtered_matches, weighted=True)
        result.type_slopes = slope_stats.get('type_slopes', {})
        result.subtype_fractions = frac_stats.get('subtype_fractions', {})
        
        # Store enhanced subtype statistics
        result.type_statistics = {
            'bttemp': security_stats.get('bttemp', result.consensus_type),
            'bsttemp': security_stats.get('bsttemp', result.best_subtype),
            'btfrac': security_stats.get('btfrac', result.consensus_type),
            'btslope': security_stats.get('btslope', result.consensus_type),
            'bstfrac': security_stats.get('bstfrac', result.best_subtype),
            'bstslope': security_stats.get('bstslope', result.best_subtype),
            'btstfrac': security_stats.get('btstfrac', result.consensus_type),
            'btstslope': security_stats.get('btstslope', result.consensus_type),
            'security_method': security_stats.get('method', 'unknown'),
            'cluster_based': security_stats.get('cluster_based', False)
        }
        
        # Set basic parameters from best match
        best_match = filtered_matches[0]
        result.r = best_match['r']
        result.lap = best_match['lap']
        result.rlap = best_match['rlap']
        result.redshift = best_match['redshift']
        result.redshift_error = best_match.get('redshift_error', 0.0)
        raw_template_name = best_match['template'].get('name', 'Unknown')
        # Clean template name to remove _epoch_X suffix
        from snid_sage.shared.utils import clean_template_name
        result.template_name = clean_template_name(raw_template_name)
        result.template_type = best_match['template'].get('type', 'Unknown')
        result.template_subtype = best_match['template'].get('subtype', '')
        result.template_age = best_match['template'].get('age', 0)
        
        # Store correlation data for plotting
        if 'correlation' in best_match:
            result.correlation = best_match['correlation'].get('correlation_full', np.array([]))
            result.redshift_axis = best_match['correlation'].get('z_axis_full', np.array([]))
        
        # Calculate confidence using new cluster-aware metrics
        type_matches = [m for m in filtered_matches if m['template'].get('type') == result.consensus_type]
        if type_matches:
            # Use RLAP-cos if available, otherwise RLAP
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            max_rlap = max(get_best_metric_value(m) for m in type_matches)
            
            # Use cluster metrics if available for confidence calculation
            if hasattr(result, 'clustering_results') and result.clustering_results:
                # Cluster-based confidence incorporates multiple factors
                cluster_metrics = type_determination.get('cluster_metrics', {})
                match_metrics = type_determination.get('match_metrics', {})
                
                if cluster_metrics:
                    # Use cluster quality and top-5 mean for confidence
                    quality_factor = {'tight': 1.0, 'moderate': 0.8, 'loose': 0.6, 'very_loose': 0.4}.get(
                        cluster_metrics.get('cluster_quality', 'loose'), 0.5)
                    top_5_factor = min(1.0, cluster_metrics.get('top_5_mean', 0.0) / 8.0)  # Normalize by good RLAP
                    size_factor = min(1.0, cluster_metrics.get('cluster_size', 0) / 10.0)  # Normalize by expected size
                    rlap_factor = min(1.0, cluster_metrics.get('mean_rlap', 0.0) / 8.0)  # Normalize by good RLAP
                    
                    result.type_confidence = (quality_factor * 0.3 + top_5_factor * 0.3 + 
                                            size_factor * 0.2 + rlap_factor * 0.2)
                elif match_metrics:
                    # Use match-based metrics for confidence
                    count_factor = min(1.0, match_metrics.get('type_match_count', 0) / 10.0)
                    rlap_factor = min(1.0, match_metrics.get('max_rlap', 0.0) / 8.0)
                    mean_rlap_factor = min(1.0, match_metrics.get('mean_rlap', 0.0) / 6.0)
                    
                    result.type_confidence = (count_factor * 0.4 + rlap_factor * 0.3 + mean_rlap_factor * 0.3)
                else:
                    # Simple fallback based on RLAP-cos
                    result.type_confidence = min(1.0, max_rlap / 8.0)
            else:
                # Simple RLAP-cos-based confidence without clustering
                result.type_confidence = min(1.0, max_rlap / 8.0)
        else:
            result.type_confidence = 0.0
            
        _LOG.info(f"Analysis complete: {result.consensus_type} (confidence: {result.type_confidence:.2f})")
        result.success = True
        report_progress(f"Analysis complete: {result.consensus_type} (confidence: {result.type_confidence:.2f})")
    else:
        # No good matches
        result.r = 0.0
        result.lap = 0.0
        result.rlap = 0.0
        result.consensus_type = 'Unknown'
        result.type_confidence = 0.0

        result.success = False
        report_progress("No good matches found")

    # Store matches for plotting - prefer clustered, thresholded, and RLAP-CCC-sorted results
    try:
        _mot = int(max_output_templates)
    except Exception:
        _mot = 5
    if _mot < 0:
        _mot = 0

    # Determine base candidates for display
    try:
        if (
            hasattr(result, 'clustering_results') and result.clustering_results and
            result.clustering_results.get('success') and result.clustering_results.get('best_cluster') and
            isinstance(result.clustering_results['best_cluster'].get('matches', []), list) and
            len(result.clustering_results['best_cluster']['matches']) > 0
        ):
            overlay_candidates = list(result.clustering_results['best_cluster']['matches'])
        elif hasattr(result, 'filtered_matches') and isinstance(result.filtered_matches, list) and result.filtered_matches:
            overlay_candidates = list(result.filtered_matches)
        else:
            overlay_candidates = list(matches)
    except Exception:
        overlay_candidates = list(matches)

    # If RLAP-CCC exists, apply the same threshold used for clustering to what we display
    try:
        any_ccc = any(('rlap_ccc' in m) for m in overlay_candidates)
        if any_ccc and isinstance(rlap_ccc_threshold, (int, float)):
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            filtered = [m for m in overlay_candidates if get_best_metric_value(m) >= float(rlap_ccc_threshold)]
            # Do NOT fallback if filtering removes all — empty list correctly signals no reliable matches
            overlay_candidates = filtered
    except Exception:
        pass

    # Sort by best available metric (prefer RLAP-CCC; fallback to RLAP)
    try:
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        overlay_candidates.sort(key=get_best_metric_value, reverse=True)
    except Exception:
        # Fallback stable sort by rlap when utilities are unavailable
        overlay_candidates.sort(key=lambda m: m.get('rlap_ccc', m.get('rlap', 0.0)), reverse=True)

    # Expose top-N to GUI
    result.best_matches = overlay_candidates[:_mot]
    result.top_matches = overlay_candidates[:_mot]
    # Store all matches separately for potential future use
    result.all_matches = matches

    # ============================================================================
    # PHASE 3: GENERATE PLOTS
    # ============================================================================
    if show_plots or save_plots:
        import matplotlib.pyplot as plt
        
        if save_plots:
            if plot_dir is None:
                plot_dir = Path('.')
            plot_dir = Path(plot_dir)
            plot_dir.mkdir(parents=True, exist_ok=True)
        
        report_progress("Generating analysis plots")
        _LOG.info("Phase 3: Generating plots...")
        
        # Generate all plots
        # NOTE: Flux and flattened spectrum plots are now generated by the CLI
        # to ensure consistency with GUI. The old plot_comparison is deprecated.
        
        # Generate clustering plots based on available results (matching GUI behavior)
        if hasattr(result, 'clustering_results') and result.clustering_results:
            try:
                from .plotting_3d import plot_cluster_statistics_summary, plot_3d_type_clustering
                
                # Generate 3D clustering visualization (like GUI)
                fig_3d_cluster = plot_3d_type_clustering(result.clustering_results)
                if save_plots:
                    fig_3d_cluster.savefig(plot_dir / 'snid_3d_clustering.png', dpi=150, bbox_inches='tight')
                
                # Generate clustering statistics summary
                fig_cluster_stats = plot_cluster_statistics_summary(result.clustering_results)
                if save_plots:
                    fig_cluster_stats.savefig(plot_dir / 'snid_clustering_statistics.png', dpi=150, bbox_inches='tight')
                    
                _LOG.info("Generated 3D clustering analysis plots")
                
            except ImportError as e:
                _LOG.warning(f"Could not generate clustering statistics plots: {e}")
        else:
            _LOG.info("No clustering results available for plotting")
        
        # Use winning cluster subtype plot like GUI does
        if hasattr(result, 'filtered_matches') and result.filtered_matches:
            from .plotting import plot_cluster_subtype_proportions
            fig_fractions = plot_cluster_subtype_proportions(result)
            if save_plots:
                fig_fractions.savefig(plot_dir / 'snid_subtype_analysis.png', dpi=150, bbox_inches='tight')
        else:
            # Fallback to original type fractions if no clustering
            fig_fractions = plot_type_fractions(result)
            if save_plots:
                fig_fractions.savefig(plot_dir / 'snid_type_fractions.png', dpi=150, bbox_inches='tight')
        
        if result.best_matches:
            # Removed - individual template correlation plots are generated by enhanced output system
            # fig_xcor = plot_correlation_function(result)
            # if save_plots:
            #     fig_xcor.savefig(plot_dir / 'snid_correlation.png', dpi=150, bbox_inches='tight')
            pass
        
        # Only plot redshift-age data if the analysis was successful
        # REMOVED: Redshift-age plot - handled by CLI interface to avoid duplicates
        # if result.success:
        #     fig_zt = plot_redshift_age(result)
        #     if save_plots:
        #         fig_zt.savefig(plot_dir / 'snid_redshift_age.png', dpi=150, bbox_inches='tight')
        
        if show_plots:
            plt.show()
        else:
            plt.close('all')

    result.runtime_sec = time.time() - tic
    report_progress(f"Analysis completed in {result.runtime_sec:.2f} seconds")
    _LOG.info(f"="*60)
    _LOG.info(f"ANALYSIS COMPLETE (runtime: {result.runtime_sec:.2f}s)")
    _LOG.info(f"="*60)
    
    return result, analysis_trace

def run_snid(
    spectrum_path: str,
    templates_dir: str,
    *,
    # ----- NEW: preprocessed spectrum input --------------------------------
    preprocessed_spectrum: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    skip_preprocessing_steps: Optional[List[str]] = None,
    # ----- user tunables -----------------------------------------------------
    zmin: float = -0.01,
    zmax: float = 1.0,
    savgol_window: int = 0,
    savgol_fwhm: float = 0.0,
    savgol_order: int = 3,
    aband_remove: bool = False,
    skyclip: bool = False,
    emclip_z: float = -1.0,
    emwidth: float = 40.0,
    wavelength_masks: Optional[List[Tuple[float, float]]] = None,
    age_range: Optional[Tuple[float, float]] = None,
    type_filter: Optional[List[str]] = None,
    template_filter: Optional[List[str]] = None,
    exclude_templates: Optional[List[str]] = None,
    apodize_percent: float = 10.0,
    peak_window_size: int = 10,
    lapmin: float = 0.3,
    rlapmin: float = 4,

    # NEW: Forced redshift parameter
    forced_redshift: Optional[float] = None,
    # ----- performance options ----------------------------------------------
    # ----- output options ----------------------------------------------------
    output_dir: str | Path | None = None,
    output_main: bool = False,
    output_fluxed: bool = False,
    output_flattened: bool = False,
    output_correlation: bool = False,
    output_plots: bool = False,
    plot_types: Optional[List[str]] = None,
    max_output_templates: int = 5,
    max_plot_templates: int = 20,
    plot_figsize: Tuple[int, int] = (10, 8),
    plot_dpi: int = 150,
    verbose: bool = False,
    # ----- plotting options -------------------------------------------------
    show_plots: bool = True,
    save_plots: bool = False,
    plot_dir: Optional[str | Path] = None
) -> Tuple[SNIDResult, Trace]:
    """Run SNID on a spectrum using modular preprocessing and analysis.
    
    This function performs template matching using cross-correlation techniques
    to identify the type, age and redshift of a supernova spectrum. It now uses
    a modular approach that separates preprocessing from correlation analysis.
    
    Example command to save everything:
    python snid/snid.py spectrum.dat templates/ --output-dir results/ --save-results --show-plots --verbose
    
    Or with all individual options:
    python snid/snid.py spectrum.dat templates/ \\
        --output-dir results/ --plot-dir plots/ \\
        --output-main --output-fluxed --output-flattened --output-correlation \\
        --save-plots --show-plots --verbose \\
        --max-output-templates 10 --rlapmin 5.0 --lapmin 0.3 \\
        --zmin -0.01 --zmax 1.0 --aband-remove --skyclip
    
    Parameters
    ----------
    spectrum_path : str
        Path to the input spectrum file
    templates_dir : str
        Path to directory containing template spectra
    preprocessed_spectrum : tuple of (np.ndarray, np.ndarray), optional
        Preprocessed spectrum (wave, flux) - if provided, skips preprocessing
    skip_preprocessing_steps : list of str, optional
        List of preprocessing steps to skip
    zmin : float, optional
        Minimum redshift to consider
    zmax : float, optional
        Maximum redshift to consider
    savgol_window : int, optional
        Savitzky-Golay filter window size in pixels (0 = no filtering)
    savgol_fwhm : float, optional
        Savitzky-Golay filter FWHM in Angstroms (alternative to window size)
    savgol_order : int, optional
        Savitzky-Golay filter polynomial order
    aband_remove : bool, optional
        Whether to remove telluric A-band
    skyclip : bool, optional
        Whether to clip sky emission lines
    emclip_z : float, optional
        Redshift at which to clip emission lines (-1 to disable)
    emwidth : float, optional
        Width in Angstroms for emission line clipping
    wavelength_masks : list of (float, float) tuples, optional
        Wavelength ranges to mask out
    age_range : tuple of (float, float), optional
        Age range in days to consider for templates
    type_filter : list of str, optional
        Only use templates of these types
    apodize_percent : float, optional
        Percentage of spectrum ends to apodize
    peak_window_size : int, optional
        Window size for finding correlation peaks
    lapmin : float, optional
        Minimum overlap fraction required
    rlapmin : float, optional
        Minimum rlap value required for a match
    output_dir : str or Path, optional
        Directory for output files
    output_main : bool, optional
        Whether to write main output file
    output_fluxed : bool, optional
        Whether to write fluxed spectrum
    output_flattened : bool, optional
        Whether to write flattened spectrum
    output_correlation : bool, optional
        Whether to write correlation function
    output_plots : bool, optional
        Whether to save plots
    plot_types : list of str, optional
        List of types to include in plots
    max_output_templates : int, optional
        Maximum number of best templates to output
    max_plot_templates : int, optional
        Maximum number of templates to include in plots
    plot_figsize : tuple of (int, int), optional
        Figure size for plots
    plot_dpi : int, optional
        DPI for plot images
    verbose : bool, optional
        Whether to print detailed information
    show_plots : bool, optional
        Whether to display plots
    save_plots : bool, optional
        Whether to save plots to files
    plot_dir : str or Path, optional
        Directory for saving plots
        
    Returns
    -------
    result : SNIDResult
        Object containing all results and matches
    trace : dict
        Dictionary with diagnostic information
    """
    
    _LOG.info("="*80)
    _LOG.info("                      SNID: SUPERNOVA IDENTIFICATION")
    _LOG.info("="*80)
    _LOG.info(f"Input spectrum: {spectrum_path}")
    _LOG.info(f"Templates directory: {templates_dir}")
    _LOG.info(f"Redshift range: {zmin:.6f} - {zmax:.6f}")
    _LOG.info(f"RLAP threshold: {rlapmin}")
    _LOG.info("="*80)
    
    full_trace = {}
    
    # ============================================================================
    # PHASE I: PREPROCESSING
    # ============================================================================
    if preprocessed_spectrum is not None:
        # Use provided preprocessed spectrum
        _LOG.info("Using provided preprocessed spectrum, skipping preprocessing phase")
        
        # Create a minimal processed_spectrum dict from the input
        wave, flux = preprocessed_spectrum
        # Use standard grid parameters for consistency with the rest of the codebase
        # Calculate DWLOG using the standard formula: log(W1/W0) / NW
        DWLOG_calculated = np.log(MAXW / MINW) / NW
        
        processed_spectrum = {
            'input_spectrum': {'wave': wave.copy(), 'flux': flux.copy()},
            'log_wave': wave,  # Assume it's already log-rebinned
            'log_flux': flux,  # Assume it's already scaled
            'flat_flux': flux,  # Assume it's already flattened
            'tapered_flux': flux,  # Assume it's already apodized
            'continuum': np.ones_like(flux),  # Dummy continuum
            'nonzero_mask': slice(0, len(flux)),
            'left_edge': 0,
            'right_edge': len(flux) - 1,
            'grid_params': {
                'NW': NW,
                'W0': MINW,
                'W1': MAXW, 
                'DWLOG': DWLOG_calculated
            }
        }
        preprocess_trace = {'preprocessed_input_used': True}
    else:
        # Run preprocessing
        input_spectrum = read_spectrum(spectrum_path) if spectrum_path else None
        
        processed_spectrum, preprocess_trace = preprocess_spectrum(
            spectrum_path=spectrum_path,
            input_spectrum=input_spectrum,
            savgol_window=savgol_window,
            savgol_fwhm=savgol_fwhm,
            savgol_order=savgol_order,
            aband_remove=aband_remove,
            skyclip=skyclip,
            emclip_z=emclip_z,
            emwidth=emwidth,
            wavelength_masks=wavelength_masks,
            apodize_percent=apodize_percent,
            skip_steps=skip_preprocessing_steps,
            verbose=verbose
        )
    
    full_trace['preprocessing'] = preprocess_trace
    
    # ============================================================================
    # PHASE II: CORRELATION ANALYSIS
    # ============================================================================
    
    # If saving plots but no plot_dir specified, use output_dir as default
    effective_plot_dir = plot_dir
    if save_plots and plot_dir is None and output_dir is not None:
        effective_plot_dir = output_dir
    
    result, analysis_trace = run_snid_analysis(
        processed_spectrum=processed_spectrum,
        templates_dir=templates_dir,
        zmin=zmin,
        zmax=zmax,
        age_range=age_range,
        type_filter=type_filter,
        template_filter=template_filter,
        exclude_templates=exclude_templates,
        peak_window_size=peak_window_size,
        lapmin=lapmin,
        rlapmin=rlapmin,
        
        forced_redshift=forced_redshift,
        max_output_templates=max_output_templates,
        verbose=verbose,

        show_plots=show_plots,
        save_plots=save_plots,
        plot_dir=effective_plot_dir
    )
    
    full_trace['analysis'] = analysis_trace
    
    # ============================================================================
    # PHASE III: OUTPUT GENERATION
    # ============================================================================
    if output_dir is not None and (output_main or output_fluxed or output_flattened or output_correlation or output_plots):
        _LOG.info("\nPhase 3: Generating output files...")
        
        # Prepare data for output files
        result.input_file = spectrum_path
        
        # Get the processed data for output
        log_wave = processed_spectrum['log_wave']
        tapered_flux = processed_spectrum['tapered_flux']  # Apodized flattened spectrum
        continuum = processed_spectrum['continuum']       # Fitted continuum
        left_edge = processed_spectrum['left_edge']
        right_edge = processed_spectrum['right_edge']
        
        if output_fluxed or output_flattened or output_correlation or output_plots:
            result.log_wave = log_wave
            
            # Fluxed output: Reconstruct flux from apodized flattened spectrum + continuum
            if output_fluxed:
                # Reconstruct the flux: (flattened + 1.0) * continuum
                reconstructed_flux = (tapered_flux + 1.0) * continuum
                result.original_flux = reconstructed_flux
            else:
                result.original_flux = None
            
            # Flattened output: Use the apodized flattened spectrum
            if output_flattened:
                result.flattened_flux = tapered_flux
            else:
                result.flattened_flux = None

        base_filename = os.path.splitext(os.path.basename(spectrum_path))[0] if spectrum_path else "spectrum"
        output_files = generate_output_files(
            result,
            output_dir=output_dir,
            base_filename=base_filename,
            output_main=output_main,
            output_fluxed=output_fluxed,
            output_flattened=output_flattened,
            output_correlation=output_correlation,
            output_plots=output_plots,
            plot_types=plot_types,
            max_templates=max_output_templates,
            max_plot_templates=max_plot_templates,
            log_wave=log_wave,
            orig_flux=result.original_flux,
            flat_flux=result.flattened_flux,
            plot_figsize=plot_figsize,
            plot_dpi=plot_dpi
        )
        result.output_files = output_files

        # Write parameter file if main output requested
        if output_main:
            params = {
                "zmin": zmin,
                "zmax": zmax,
                "savgol_window": savgol_window,
                "savgol_fwhm": savgol_fwhm,
                "savgol_order": savgol_order,
                "aband_remove": int(aband_remove),
                "skyclip": int(skyclip),
                "emclip_z": emclip_z,
                "emwidth": emwidth,
                "lapmin": lapmin,
                "rlapmin": rlapmin,
        
                "apodize_percent": apodize_percent,
                "output_plots": int(output_plots),
                "max_plot_templates": max_plot_templates
            }
            if age_range:
                params["age_min"] = age_range[0]
                params["age_max"] = age_range[1]
            if plot_types:
                params["plot_types"] = " ".join(plot_types)
            
            param_file = os.path.join(output_dir, f"{base_filename}_snid.param")
            write_parameter_file(params, param_file)
            _LOG.info(f"  Wrote parameter file: {param_file}")
        
        # Print summary of generated files
        if output_plots and 'plots' in output_files:
            plots_generated = output_files['plots']
            total_plots = sum(len(plot_list) for plot_list in plots_generated.values())
            _LOG.info(f"  Generated {total_plots} plots across {len(plots_generated)} types")
            for plot_type, plot_list in plots_generated.items():
                _LOG.info(f"    {plot_type}: {len(plot_list)} plots")
        
        if output_correlation and 'template_data' in output_files:
            template_data = output_files['template_data']
            corr_files = template_data.get('correlation_files', {})
            spectra_files = template_data.get('spectra_files', {})
            _LOG.info(f"  Generated correlation data for {len(corr_files)} templates")
            _LOG.info(f"  Generated spectral data for {len(spectra_files)} templates")

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    _LOG.info("\n" + "="*80)
    _LOG.info("                             FINAL SUMMARY")
    _LOG.info("="*80)
    
    if result.success:
        _LOG.info(f"[SUCCESS] ANALYSIS SUCCESSFUL")
        _LOG.info(f"   Best type: {result.consensus_type}")
        _LOG.info(f"   Best template: {result.template_name}")
        _LOG.info(f"   Redshift: {result.redshift:.5f} ± {result.redshift_error:.5f}")
        _LOG.info(f"   RLAP: {result.rlap:.2f}")
        _LOG.info(f"   Confidence: {result.type_confidence:.2f}")
    
    else:
        _LOG.error(f"[FAILED] NO GOOD MATCH FOUND")
        _LOG.error(f"   Try lowering rlapmin or adjusting redshift range")
    
    _LOG.info(f"   Runtime: {result.runtime_sec:.2f} seconds")
    _LOG.info("="*80)

    return result, full_trace

# ----------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="SNID: Supernova Identification")
    
    # Required arguments
    parser.add_argument("spectrum_path", help="Path to the input spectrum file")
    parser.add_argument("templates_dir", help="Path to directory containing template spectra")
    
    # Optional arguments
    parser.add_argument("--output-dir", "-o", help="Directory for output files")
    parser.add_argument("--zmin", type=float, default=-0.01, help="Minimum redshift to consider")
    parser.add_argument("--zmax", type=float, default=1.0, help="Maximum redshift to consider")
    parser.add_argument("--rlapmin", type=float, default=4.0, help="Minimum rlap value required")
    parser.add_argument("--lapmin", type=float, default=0.3, help="Minimum overlap fraction required")
    parser.add_argument("--aband-remove", action="store_true", help="Remove telluric A-band")
    parser.add_argument("--skyclip", action="store_true", help="Clip sky emission lines")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed information")
    parser.add_argument("--show-plots", action="store_true", help="Display plots")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to files")
    parser.add_argument("--plot-dir", help="Directory for saving plots")
    parser.add_argument("--output-main", action="store_true", help="Write main output file")
    parser.add_argument("--output-fluxed", action="store_true", help="Write fluxed spectrum")
    parser.add_argument("--output-flattened", action="store_true", help="Write flattened spectrum")
    parser.add_argument("--output-correlation", action="store_true", help="Write correlation function")
    parser.add_argument("--max-output-templates", type=int, default=10, help="Maximum number of best templates to output")
    parser.add_argument("--save-results", action="store_true", help="Save results to files")

    args = parser.parse_args()

    # Run SNID with command line arguments
    try:
        result, trace = run_snid(
            spectrum_path=args.spectrum_path,
            templates_dir=args.templates_dir,
            output_dir=args.output_dir,
            zmin=args.zmin,
            zmax=args.zmax,
            rlapmin=args.rlapmin,
            lapmin=args.lapmin,
            aband_remove=args.aband_remove,
            skyclip=args.skyclip,
            verbose=args.verbose,
            show_plots=args.show_plots,
            save_plots=args.save_plots or args.save_results,  # Save plots if either flag is set
            plot_dir=args.plot_dir,
            output_main=args.output_main or args.save_results,  # Save main output if either flag is set
            output_fluxed=args.output_fluxed or args.save_results,  # Save fluxed spectrum if either flag is set
            output_flattened=args.output_flattened or args.save_results,  # Save flattened spectrum if either flag is set
            output_correlation=args.output_correlation or args.save_results,  # Save correlation if either flag is set
            max_output_templates=args.max_output_templates
        )

    except Exception as e:
        _LOG.error(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

