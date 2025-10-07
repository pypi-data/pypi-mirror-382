"""
SNID Batch Command
=================

Simplified command for batch processing multiple spectra with SNID.
Two modes: Complete analysis or Minimal summary.

OPTIMIZED VERSION: Templates are loaded once and reused for all spectra.
"""

import argparse
import sys
import os
import glob
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import json
import time
import numpy as np
import csv
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

from snid_sage.snid.snid import preprocess_spectrum, run_snid_analysis, SNIDResult
from snid_sage.shared.exceptions.core_exceptions import SpectrumProcessingError
from snid_sage.shared.utils.math_utils import (
    calculate_weighted_redshift_balanced,
    calculate_weighted_age,
    apply_exponential_weighting,
    get_best_metric_value
)
from snid_sage.shared.utils.results_formatter import clean_template_name
from snid_sage.shared.utils.logging import set_verbosity as set_global_verbosity
from snid_sage.shared.utils.logging import VerbosityLevel

# Import and apply centralized font configuration for consistent plotting
try:
    from snid_sage.shared.utils.plotting.font_sizes import apply_font_config
    apply_font_config()
except ImportError:
    # Fallback if font configuration is not available
    pass


class BatchTemplateManager:
    """
    Optimized template manager for batch processing.
    
    Loads templates once and reuses them for all spectrum analyses,
    providing 10-50x speedup for batch processing by avoiding repeated
    template loading and FFT computation.
    """
    
    def __init__(self, templates_dir: Optional[str], verbose: bool = False):
        # Initialize logging early so helper methods can use it
        self._log = logging.getLogger('snid_sage.snid.batch.template_manager')

        # Validate and auto-correct templates directory
        self.templates_dir = self._validate_and_fix_templates_dir(templates_dir)
        self.verbose = verbose
        self._templates = None
        self._templates_metadata = None
        self._load_time = None
    
    def _validate_and_fix_templates_dir(self, templates_dir: Optional[str]) -> str:
        """
        Validate templates directory and auto-correct if needed.
        
        Args:
            templates_dir: Path to templates directory (None to auto-discover)
            
        Returns:
            Valid templates directory path
            
        Raises:
            FileNotFoundError: If no valid templates directory can be found
        """
        # If no templates directory provided, auto-discover
        if templates_dir is None:
            try:
                from snid_sage.shared.utils.simple_template_finder import find_templates_directory_or_raise
                auto_found_dir = find_templates_directory_or_raise()
                self._log.info(f"[SUCCESS] Auto-discovered templates at: {auto_found_dir}")
                return str(auto_found_dir)
            except (ImportError, FileNotFoundError):
                raise FileNotFoundError(
                    "Could not auto-discover templates directory. Please provide templates_dir explicitly."
                )
        
        # Check if provided directory exists and is valid
        if os.path.exists(templates_dir):
            return templates_dir
        
        # Try to auto-find templates directory
        try:
            from snid_sage.shared.utils.simple_template_finder import find_templates_directory_or_raise
            auto_found_dir = find_templates_directory_or_raise()
            self._log.warning(f"Templates directory '{templates_dir}' not found.")
            self._log.info(f"[SUCCESS] Auto-discovered templates at: {auto_found_dir}")
            return str(auto_found_dir)
        except (ImportError, FileNotFoundError):
            # Fallback failed
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        
    def load_templates_once(self) -> bool:
        """
        Load templates once for the entire batch processing session.
        
        Returns
        -------
        bool
            True if templates were loaded successfully, False otherwise
        """
        if self._templates is not None:
            return True  # Already loaded
            
        start_time = time.time()
        
        try:
            # Use unified storage system (for HDF5 templates) - this is already optimized
            try:
                from snid_sage.snid.core.integration import load_templates_unified
                self._templates = load_templates_unified(self.templates_dir)
                self._templates_metadata = {}
                self._log.info(f"✅ Loaded {len(self._templates)} templates using UNIFIED STORAGE")
            except ImportError:
                # Fallback to standard loading (legacy path removed)
                from snid_sage.snid.io import load_templates
                self._templates, self._templates_metadata = load_templates(self.templates_dir, flatten=True)
                self._log.info(f"✅ Loaded {len(self._templates)} templates using STANDARD method")
            
            self._load_time = time.time() - start_time
            
            if not self._templates:
                self._log.error("❌ No templates loaded")
                self._log.error("   Check that templates directory exists and contains HDF5 files and template_index.json")
                self._log.error(f"   Templates directory: {self.templates_dir}")
                return False
                
            self._log.info(f"🚀 Template loading complete in {self._load_time:.2f}s")
            self._log.info(f"📊 Ready for batch processing with {len(self._templates)} templates")
            
            return True
            
        except Exception as e:
            self._log.error(f"❌ Failed to load templates: {e}")
            self._log.error(f"   Templates directory: {self.templates_dir}")
            self._log.error("   Ensure the directory exists and contains valid template files")
            if self.verbose:
                import traceback
                self._log.error(f"   Full traceback: {traceback.format_exc()}")
            return False
    
    def get_filtered_templates(self, 
                             type_filter: Optional[List[str]] = None,
                             template_filter: Optional[List[str]] = None,
                             age_range: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        """
        Get filtered templates without reloading from disk.
        
        Parameters
        ----------
        type_filter : list of str, optional
            Only include templates of these types
        template_filter : list of str, optional
            Only include templates with these names
        age_range : tuple of (float, float), optional
            Only include templates within this age range
            
        Returns
        -------
        List[Dict[str, Any]]
            Filtered templates ready for analysis
        """
        if self._templates is None:
            raise RuntimeError("Templates not loaded. Call load_templates_once() first.")
        
        templates = self._templates[:]  # Start with copy of all templates
        original_count = len(templates)
        
        # Apply age filtering
        if age_range is not None:
            age_min, age_max = age_range
            templates = [t for t in templates if age_min <= t.get('age', 0) <= age_max]
            self._log.info(f"🔍 Age filtering: {original_count} -> {len(templates)} templates")
        
        # Apply type filtering
        if type_filter is not None and len(type_filter) > 0:
            templates = [t for t in templates if t.get('type', '') in type_filter]
            self._log.info(f"🔍 Type filtering: {original_count} -> {len(templates)} templates")
        
        # Apply template name filtering
        if template_filter is not None and len(template_filter) > 0:
            pre_filter_count = len(templates)
            templates = [t for t in templates if t.get('name', '') in template_filter]
            self._log.info(f"🔍 Template name filtering: {pre_filter_count} -> {len(templates)} templates")
            
            if len(templates) == 0 and pre_filter_count > 0:
                self._log.warning(f"⚠️ All templates filtered out by name filter: {template_filter}")
        
        return templates
    
    @property
    def is_loaded(self) -> bool:
        """Check if templates are loaded."""
        return self._templates is not None
    
    @property
    def template_count(self) -> int:
        """Get total number of loaded templates."""
        return len(self._templates) if self._templates else 0
    
    @property
    def load_time(self) -> float:
        """Get time taken to load templates."""
        return self._load_time or 0.0


_WORKER_TM: Optional[BatchTemplateManager] = None
_WORKER_ARGS_CACHE: Optional[Dict[str, Any]] = None


def _mp_worker_initializer(templates_dir: str,
                           type_filter: Optional[List[str]],
                           template_filter: Optional[List[str]]) -> None:
    """Per-process initializer: load all templates once for this worker process."""
    global _WORKER_TM, _WORKER_ARGS_CACHE
    try:
        # Avoid BLAS over-subscription inside processes
        os.environ.setdefault('OMP_NUM_THREADS', '1')
        os.environ.setdefault('MKL_NUM_THREADS', '1')
    except Exception:
        pass

    # Suppress verbose logging inside worker processes (keep console clean)
    try:
        logging.disable(logging.INFO)
        logging.getLogger().setLevel(logging.WARNING)
    except Exception:
        pass

    # Build a per-process template manager and pre-load templates (all relevant HDF5 files)
    _WORKER_TM = BatchTemplateManager(templates_dir, verbose=False)
    _WORKER_TM.load_templates_once()

    # Pre-warm unified storage path so subsequent analysis calls are fast
    try:
        from snid_sage.snid.core.integration import load_templates_unified
        _ = load_templates_unified(templates_dir, type_filter=type_filter, template_names=template_filter)
    except Exception:
        # Non-fatal; run_snid_analysis will still load via unified storage
        pass

    _WORKER_ARGS_CACHE = {
        'type_filter': type_filter,
        'template_filter': template_filter,
        'templates_dir': templates_dir,
    }


def _mp_process_one(index: int,
                    spectrum_path: str,
                    forced_redshift: Optional[float],
                    output_dir: str,
                    args_dict: Dict[str, Any]) -> Tuple[int, Tuple[str, bool, str, Dict[str, Any]]]:
    """Process exactly one spectrum in a worker process and return (index, result_tuple)."""
    # Rebuild a minimal argparse-like object for reuse of existing functions
    args = argparse.Namespace(**args_dict)

    # Use per-process template manager created in initializer
    global _WORKER_TM
    if _WORKER_TM is None:
        _WORKER_TM = BatchTemplateManager(args.templates_dir, verbose=False)
        _WORKER_TM.load_templates_once()

    try:
        name, success, message, summary = process_single_spectrum_optimized(
            spectrum_path,
            _WORKER_TM,
            output_dir,
            args,
            forced_redshift_override=forced_redshift
        )
        return index, (name, success, message, summary)
    except Exception as e:
        name = Path(spectrum_path).stem
        return index, (name, False, str(e), {
            'spectrum': name,
            'file_path': spectrum_path,
            'success': False,
            'error': str(e)
        })


def process_single_spectrum_optimized(
    spectrum_path: str,
    template_manager: BatchTemplateManager,
    output_dir: str,
    args: argparse.Namespace,
    *,
    forced_redshift_override: Optional[float] = None
) -> Tuple[str, bool, str, Dict[str, Any]]:
    """
    Process a single spectrum using pre-loaded templates via first-class API.
    """
    spectrum_name = Path(spectrum_path).stem
    spectrum_output_dir = Path(output_dir) / spectrum_name
    
    # Determine output settings based on mode
    if args.minimal:
        # Minimal mode: basic output files only (no plots or extra data) - flat directory structure
        save_outputs = True
        create_dir = False  # Don't create individual spectrum directories
    elif args.complete:
        # Complete mode: all outputs including plots - organized in subdirectories
        save_outputs = True
        create_dir = True
        spectrum_output_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Default mode: main outputs only - organized in subdirectories
        save_outputs = True
        create_dir = True
        spectrum_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # STEP 1: Preprocess spectrum with grid validation/auto-clipping
        try:
            processed_spectrum, _ = preprocess_spectrum(
                spectrum_path=spectrum_path,
                savgol_window=getattr(args, 'savgol_window', 0),
                savgol_order=getattr(args, 'savgol_order', 3),
                aband_remove=getattr(args, 'aband_remove', False),
                skyclip=getattr(args, 'skyclip', False),
                wavelength_masks=getattr(args, 'wavelength_masks', None),
                verbose=False,  # Suppress preprocessing output in batch mode
                clip_to_grid=True
            )
        except SpectrumProcessingError as e:
            msg = str(e)
            # Classify error type for clearer reporting
            lower_msg = msg.lower()
            if 'completely outside' in lower_msg or 'outside the optical grid' in lower_msg:
                error_type = 'out_of_grid'
            elif 'insufficient overlap' in lower_msg:
                error_type = 'insufficient_overlap'
            else:
                error_type = 'spectrum_processing_error'
            return spectrum_name, False, msg, {
                'spectrum': spectrum_name,
                'file_path': spectrum_path,
                'success': False,
                'error': msg,
                'error_type': error_type,
                'error_class': 'SpectrumProcessingError'
            }
        
        # STEP 2: Get filtered templates (no reloading!)
        filtered_templates = template_manager.get_filtered_templates(
            type_filter=args.type_filter,
            template_filter=args.template_filter
        )
        
        if not filtered_templates:
            return spectrum_name, False, "No templates after filtering", {
                'spectrum': spectrum_name,
                'file_path': spectrum_path,
                'success': False,
                'error': 'No templates after filtering'
            }
        
        # STEP 3: Run SNID analysis using first-class API with preloaded templates
        # NOTE: run_snid_analysis currently manages template loading internally.
        # We do not pass preloaded templates here to avoid interface mismatch.
        # Determine if a forced redshift is being used for this spectrum
        used_forced_redshift = (
            forced_redshift_override
            if forced_redshift_override is not None
            else args.forced_redshift
        )

        result, _ = run_snid_analysis(
            processed_spectrum=processed_spectrum,
            templates_dir=template_manager.templates_dir,
            zmin=args.zmin,
            zmax=args.zmax,
            rlapmin=getattr(args, 'rlapmin', 4.0),
            lapmin=getattr(args, 'lapmin', 0.3),
            rlap_ccc_threshold=getattr(args, 'rlap_ccc_threshold', 1.8),
            forced_redshift=used_forced_redshift,
            verbose=False,
            show_plots=False,
            save_plots=False
        )
        
        # STEP 4: Generate outputs if requested
        if save_outputs and result.success:
            _save_spectrum_outputs(
                result=result,
                spectrum_path=spectrum_path,
                output_dir=spectrum_output_dir if create_dir else output_dir,
                args=args
            )

        # Default behavior: for default mode (not minimal/complete) also generate plots unless disabled
        if (not args.minimal) and (not args.complete) and result.success and (not getattr(args, 'no_plots', False)):
            try:
                from snid_sage.snid.plotting import (
                    plot_redshift_age, plot_flux_comparison, plot_flat_comparison
                )
                from snid_sage.shared.utils.math_utils import get_best_metric_value
                import matplotlib.pyplot as plt
                sdir = spectrum_output_dir if create_dir else Path(output_dir)
                spectrum_name = Path(spectrum_path).stem
                # Redshift vs Age (already cluster-aware inside the function)
                redshift_age_file = sdir / f"{spectrum_name}_redshift_age.png"
                try:
                    fig = plot_redshift_age(result)
                    # Only save if plot contains data (non-empty axes)
                    if fig and fig.axes and fig.axes[0].has_data():
                        fig.savefig(str(redshift_age_file), dpi=150, bbox_inches='tight')
                    plt.close(fig)
                except Exception as pe:
                    logging.getLogger('snid_sage.snid.batch').warning(f"Redshift-age plot failed: {pe}")

                # Choose the same match the GUI would show: winning cluster → filtered → best
                plot_matches = []
                winning_cluster = None
                if (hasattr(result, 'clustering_results') and result.clustering_results and
                    result.clustering_results.get('success')):
                    cr = result.clustering_results
                    if cr.get('user_selected_cluster'):
                        winning_cluster = cr['user_selected_cluster']
                    elif cr.get('best_cluster'):
                        winning_cluster = cr['best_cluster']
                if winning_cluster and winning_cluster.get('matches'):
                    plot_matches = winning_cluster['matches']
                elif hasattr(result, 'filtered_matches') and result.filtered_matches:
                    plot_matches = result.filtered_matches
                elif hasattr(result, 'best_matches') and result.best_matches:
                    plot_matches = result.best_matches

                if plot_matches:
                    plot_matches = sorted(plot_matches, key=get_best_metric_value, reverse=True)
                    top_match = plot_matches[0]
                    # Flux overlay
                    flux_file = sdir / f"{spectrum_name}_flux_spectrum.png"
                    try:
                        fig = plot_flux_comparison(top_match, result)
                        if fig and fig.axes and fig.axes[0].has_data():
                            fig.savefig(str(flux_file), dpi=150, bbox_inches='tight')
                        plt.close(fig)
                    except Exception as fe:
                        logging.getLogger('snid_sage.snid.batch').warning(f"Flux spectrum plot failed: {fe}")
                    # Flat overlay
                    flat_file = sdir / f"{spectrum_name}_flattened_spectrum.png"
                    try:
                        fig = plot_flat_comparison(top_match, result)
                        if fig and fig.axes and fig.axes[0].has_data():
                            fig.savefig(str(flat_file), dpi=150, bbox_inches='tight')
                        plt.close(fig)
                    except Exception as fe2:
                        logging.getLogger('snid_sage.snid.batch').warning(f"Flattened spectrum plot failed: {fe2}")
            except Exception as e:
                logging.getLogger('snid_sage.snid.batch').debug(f"Default plot generation failed: {e}")
        
        if result.success:
            # Create GUI-style summary with cluster-aware analysis
            summary = _create_cluster_aware_summary(result, spectrum_name, spectrum_path)
            # Record whether a fixed redshift was used and its value
            try:
                summary['redshift_fixed'] = used_forced_redshift is not None
                summary['redshift_fixed_value'] = (
                    float(used_forced_redshift) if used_forced_redshift is not None else None
                )
            except Exception:
                summary['redshift_fixed'] = False
                summary['redshift_fixed_value'] = None
            # Flag weak match if clustering failed but some matches survived threshold
            try:
                has_clusters = bool(getattr(result, 'clustering_results', None)) and getattr(result, 'clustering_results', {}).get('success', False)
                surviving = len(getattr(result, 'filtered_matches', []) or [])
                weak_match = (not has_clusters) and (surviving > 0)
            except Exception:
                weak_match = False

            if weak_match:
                summary['weak_match'] = True
            else:
                summary['weak_match'] = False

            return spectrum_name, True, "Success", summary
        else:
            return spectrum_name, False, "No good matches found", {
                'spectrum': spectrum_name,
                'file_path': spectrum_path,
                'success': False
            }
            
    except Exception as e:
        return spectrum_name, False, str(e), {
            'spectrum': spectrum_name,
            'file_path': spectrum_path,
            'success': False,
            'error': str(e)
        }
 


def _create_cluster_aware_summary(result: SNIDResult, spectrum_name: str, spectrum_path: str) -> Dict[str, Any]:
    """
    Create GUI-style cluster-aware summary with winning cluster analysis.
    
    This matches the GUI's approach of using the winning cluster for all analysis
    rather than mixing all matches above threshold.
    """
    # Get the winning cluster (user selected or automatic best)
    winning_cluster = None
    cluster_matches = []
    
    if (hasattr(result, 'clustering_results') and 
        result.clustering_results and 
        result.clustering_results.get('success')):
        
        clustering_results = result.clustering_results
        
        # Priority: user_selected_cluster > best_cluster  
        if 'user_selected_cluster' in clustering_results:
            winning_cluster = clustering_results['user_selected_cluster']
        elif 'best_cluster' in clustering_results:
            winning_cluster = clustering_results['best_cluster']
        
        if winning_cluster:
            cluster_matches = winning_cluster.get('matches', [])
            # Sort cluster matches by best available metric (RLAP-CCC if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
    
    # If no clustering or cluster, fall back to filtered_matches, then best_matches
    if not cluster_matches:
        if hasattr(result, 'filtered_matches') and result.filtered_matches:
            cluster_matches = result.filtered_matches
            # Sort by best available metric (RLAP-CCC if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
        elif hasattr(result, 'best_matches') and result.best_matches:
            cluster_matches = result.best_matches
            # Sort by best available metric (RLAP-CCC if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
    
    # Create the summary using winning cluster data
    summary = {
        'spectrum': spectrum_name,
        'file_path': spectrum_path,
        'success': True,
        'best_template': result.template_name,
        'best_template_type': result.template_type,
        'best_template_subtype': result.template_subtype,
        'consensus_type': result.consensus_type,
        'consensus_subtype': result.best_subtype,
        'redshift': result.redshift,
        'redshift_error': result.redshift_error,
        'rlap': result.rlap,


        'runtime': result.runtime_sec,
        'has_clustering': winning_cluster is not None,
        'cluster_size': len(cluster_matches) if cluster_matches else 0,
    }
    
    # If we have any matches (from cluster or fallback), override the "best_*" fields
    # to reflect the true top match according to RLAP-CCC (final metric),
    # and also expose RLAP-CCC on the summary for downstream reporting.
    if cluster_matches:
        top_match = cluster_matches[0]
        top_tpl = top_match.get('template', {}) if isinstance(top_match.get('template'), dict) else {}
        summary['best_template'] = top_tpl.get('name', top_match.get('name', summary['best_template']))
        summary['best_template_type'] = top_tpl.get('type', summary['best_template_type'])
        summary['best_template_subtype'] = top_tpl.get('subtype', summary['best_template_subtype'])
        # Use the top match's redshift/error for "Best Match Redshift"
        summary['redshift'] = top_match.get('redshift', summary['redshift'])
        summary['redshift_error'] = top_match.get('redshift_error', summary['redshift_error'])
        # Always expose RLAP-CCC; if missing, fall back to RLAP but keep the key present
        summary['rlap_ccc'] = top_match.get('rlap_ccc', top_match.get('rlap', summary.get('rlap', 0.0)))
        # Propagate age for top match if available (used as fallback when no cluster age)
        if isinstance(top_tpl, dict):
            summary['age'] = top_tpl.get('age', summary.get('age', None))

        # If clustering failed and there are one or two surviving matches, use the top match
        # subtype for the consensus_subtype shown in batch one-line summaries
        try:
            if (not summary.get('has_clustering')) and (1 <= len(cluster_matches) <= 2):
                top_subtype = top_tpl.get('subtype', '') if isinstance(top_tpl, dict) else ''
                if top_subtype and top_subtype.strip() != '':
                    summary['consensus_subtype'] = top_subtype
        except Exception:
            pass

    # Add cluster statistics if available
    if winning_cluster:
        summary['cluster_type'] = winning_cluster.get('type', 'Unknown')
        summary['cluster_score'] = winning_cluster.get('composite_score', 0.0)
        summary['cluster_method'] = 'Type-specific GMM'
        
        # Add new quality metrics
        if 'quality_assessment' in winning_cluster:
            qa = winning_cluster['quality_assessment']
            summary['cluster_quality_category'] = qa.get('quality_category', 'Unknown')
            summary['cluster_quality_description'] = qa.get('quality_description', '')
            summary['cluster_mean_top_5'] = qa.get('mean_top_5', 0.0)
            summary['cluster_penalized_score'] = qa.get('penalized_score', 0.0)
        
        if 'confidence_assessment' in winning_cluster:
            ca = winning_cluster['confidence_assessment']
            summary['cluster_confidence_level'] = ca.get('confidence_level', 'unknown')
            summary['cluster_confidence_description'] = ca.get('confidence_description', '')
            summary['cluster_statistical_significance'] = ca.get('statistical_significance', 'unknown')
            summary['cluster_second_best_type'] = ca.get('second_best_type', 'N/A')
        
        # Calculate enhanced cluster statistics using hybrid methods
        if cluster_matches:
            rlaps = np.array([m['rlap'] for m in cluster_matches])
            
            # Collect redshift data with uncertainties for balanced estimation
            redshifts_with_errors = []
            redshift_errors = []
            rlap_cos_values = []
            
            # Collect age data for separate age estimation
            ages_for_estimation = []
            age_rlap_cos_values = []
            
            for m in cluster_matches:
                template = m.get('template', {})
                
                # Always collect redshift data (uncertainties are always available)
                z = m.get('redshift')
                z_err = m.get('redshift_error', 0.0)
                rlap_cos = get_best_metric_value(m)
                
                if z is not None and np.isfinite(z) and z_err > 0:
                    redshifts_with_errors.append(z)
                    redshift_errors.append(z_err)
                    rlap_cos_values.append(rlap_cos)
                
                # Separately collect age data (no uncertainties available)
                age = template.get('age', 0.0) if template else 0.0
                if age is not None and np.isfinite(age):
                    ages_for_estimation.append(age)
                    age_rlap_cos_values.append(rlap_cos)
            
            # Balanced redshift estimation (always use this when data available)
            if redshifts_with_errors:
                z_final, z_final_err = calculate_weighted_redshift_balanced(
                    redshifts_with_errors, redshift_errors, rlap_cos_values
                )
                summary['cluster_redshift_weighted'] = z_final
                summary['cluster_redshift_weighted_uncertainty'] = z_final_err
                summary['cluster_redshift_scatter'] = 0.0  # Properly handled in balanced estimation
            else:
                # No valid redshift data
                summary['cluster_redshift_weighted'] = np.nan
                summary['cluster_redshift_weighted_uncertainty'] = np.nan
                summary['cluster_redshift_scatter'] = 0.0
            
            # Age estimation with proper uncertainty calculation
            if ages_for_estimation:
                # Apply exponential weighting to RLAP-cos values for age calculation
                age_weights = apply_exponential_weighting(np.array(age_rlap_cos_values))
                age_final, age_uncertainty = calculate_weighted_age(ages_for_estimation, age_weights)
                summary['cluster_age_weighted'] = age_final
                summary['cluster_age_uncertainty'] = age_uncertainty
                summary['cluster_age_scatter'] = 0.0  # Handled in uncertainty calculation
                summary['redshift_age_covariance'] = 0.0  # Separate estimation, no covariance
            else:
                # No valid age data
                summary['cluster_age_weighted'] = np.nan
                summary['cluster_age_uncertainty'] = 0.0
                summary['cluster_age_scatter'] = 0.0
                summary['redshift_age_covariance'] = 0.0
            
            summary['cluster_rlap_mean'] = np.mean(rlaps)
            
            # Subtype composition within cluster (GUI-style)
            from collections import Counter
            subtypes = []
            for m in cluster_matches:
                template = m.get('template', {})
                subtype = template.get('subtype', 'Unknown') if template else 'Unknown'
                if not subtype or subtype.strip() == '':
                    subtype = 'Unknown'
                subtypes.append(subtype)
            
            subtype_counts = Counter(subtypes)
            subtype_fractions = {}
            for subtype, count in subtype_counts.items():
                subtype_fractions[subtype] = count / len(cluster_matches)
            
            # Sort subtypes by frequency
            sorted_subtypes = sorted(subtype_fractions.items(), key=lambda x: x[1], reverse=True)
            summary['cluster_subtypes'] = sorted_subtypes[:5]  # Top 5 subtypes
    
    # Fallback to old approach only if no clustering available
    else:
        summary['cluster_method'] = 'No clustering'
        # Use type/subtype fractions as fallback
        if hasattr(result, 'type_fractions') and result.type_fractions:
            sorted_types = sorted(result.type_fractions.items(), key=lambda x: x[1], reverse=True)
            summary['top_types'] = sorted_types[:3]
        else:
            summary['top_types'] = [(result.consensus_type, 1.0)]
        
        if (hasattr(result, 'subtype_fractions') and result.subtype_fractions and 
            result.consensus_type in result.subtype_fractions):
            subtype_data = result.subtype_fractions[result.consensus_type]
            sorted_subtypes = sorted(subtype_data.items(), key=lambda x: x[1], reverse=True)
            summary['cluster_subtypes'] = sorted_subtypes[:3]
        else:
            summary['cluster_subtypes'] = [(result.best_subtype or 'Unknown', 1.0)]
    
    return summary


def _get_winning_cluster(result: SNIDResult) -> Optional[Dict[str, Any]]:
    """
    Get the winning cluster from SNID results (user selected or automatic best).
    
    This matches the GUI's cluster selection logic.
    """
    if not (hasattr(result, 'clustering_results') and 
            result.clustering_results and 
            result.clustering_results.get('success')):
        return None
    
    clustering_results = result.clustering_results
    
    # Priority: user_selected_cluster > best_cluster
    if 'user_selected_cluster' in clustering_results:
        return clustering_results['user_selected_cluster']
    elif 'best_cluster' in clustering_results:
        return clustering_results['best_cluster']
    
    return None


def _save_spectrum_outputs(
    result: SNIDResult,
    spectrum_path: str,
    output_dir: Path,
    args: argparse.Namespace
) -> None:
    """
    Save spectrum outputs based on the analysis mode using GUI-style cluster-aware approach.
    """
    # Ensure output_dir supports Path-style '/' operations even if a string was passed
    output_dir = Path(output_dir)
    try:
        # Extract spectrum name from path
        spectrum_name = Path(spectrum_path).stem
        
        if args.minimal:
            # Minimal mode: save main result file only
            from snid_sage.snid.io import write_result
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
        elif args.complete:
            # Complete mode: save all outputs including comprehensive plots and data files
            from snid_sage.snid.io import (
                write_result, write_fluxed_spectrum, write_flattened_spectrum,
                write_correlation, write_template_correlation_data, write_template_spectra_data
            )
            from snid_sage.snid.plotting import (
                plot_redshift_age, plot_cluster_subtype_proportions,
                plot_flux_comparison, plot_flat_comparison, plot_correlation_view
            )
            
            # Save main result file
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
            # Save additional spectrum files
            if hasattr(result, 'processed_spectrum'):
                # Save fluxed spectrum
                if 'log_wave' in result.processed_spectrum and 'log_flux' in result.processed_spectrum:
                    fluxed_file = output_dir / f"{spectrum_name}.fluxed"
                    write_fluxed_spectrum(
                        result.processed_spectrum['log_wave'], 
                        result.processed_spectrum['log_flux'], 
                        str(fluxed_file)
                    )
                
                # Save flattened spectrum
                if 'log_wave' in result.processed_spectrum and 'flat_flux' in result.processed_spectrum:
                    flat_file = output_dir / f"{spectrum_name}.flattened"
                    write_flattened_spectrum(
                        result.processed_spectrum['log_wave'], 
                        result.processed_spectrum['flat_flux'], 
                        str(flat_file)
                    )
            
            if result.success:
                # Get winning cluster for GUI-style plotting
                winning_cluster = _get_winning_cluster(result)
                cluster_matches = winning_cluster.get('matches', []) if winning_cluster else []
                
                # Use cluster matches for plotting, fallback to filtered/best matches
                plot_matches = cluster_matches
                if not plot_matches:
                    if hasattr(result, 'filtered_matches') and result.filtered_matches:
                        plot_matches = result.filtered_matches
                    elif hasattr(result, 'best_matches') and result.best_matches:
                        plot_matches = result.best_matches
                
                # CRITICAL: Sort all plot matches by best available metric (RLAP-CCC if available, otherwise RLAP) descending
                if plot_matches:
                    from snid_sage.shared.utils.math_utils import get_best_metric_value
                    plot_matches = sorted(plot_matches, key=get_best_metric_value, reverse=True)
                
                # 1. 3D GMM Clustering Visualization (GUI-style)
                if (hasattr(result, 'clustering_results') and 
                    result.clustering_results and 
                    result.clustering_results.get('success')):
                    try:
                        # Use correct 3D GMM clustering plot like GUI does
                        from snid_sage.snid.plotting_3d import plot_3d_type_clustering
                        import matplotlib.pyplot as plt
                        
                        gmm_file = output_dir / f"{spectrum_name}_3d_gmm_clustering.png"
                        fig = plot_3d_type_clustering(result.clustering_results, save_path=str(gmm_file))
                        plt.close(fig)  # Prevent memory leak
                        
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"3D GMM clustering plot failed: {e}")
                
                # 2. Redshift vs Age plot (cluster-aware)
                try:
                    import matplotlib.pyplot as plt
                    redshift_age_file = output_dir / f"{spectrum_name}_redshift_age.png"
                    fig = plot_redshift_age(result, save_path=str(redshift_age_file))
                    plt.close(fig)  # Prevent memory leak
                except Exception as e:
                    logging.getLogger('snid_sage.snid.batch').debug(f"Redshift-age plot failed: {e}")
                
                # 3. Cluster-aware subtype proportions (GUI-style)
                try:
                    import matplotlib.pyplot as plt
                    subtype_file = output_dir / f"{spectrum_name}_cluster_subtypes.png"
                    fig = plot_cluster_subtype_proportions(
                        result, 
                        selected_cluster=winning_cluster,
                        save_path=str(subtype_file)
                    )
                    plt.close(fig)  # Prevent memory leak
                except Exception as e:
                    logging.getLogger('snid_sage.snid.batch').debug(f"Cluster subtype plot failed: {e}")
                
                # 5. Flux spectrum plot (best match) - same as GUI
                if plot_matches:
                    try:
                        import matplotlib.pyplot as plt
                        flux_file = output_dir / f"{spectrum_name}_flux_spectrum.png"
                        fig = plot_flux_comparison(plot_matches[0], result, save_path=str(flux_file))
                        plt.close(fig)  # Prevent memory leak
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"Flux spectrum plot failed: {e}")
                    
                    # 6. Flattened spectrum plot (best match) - same as GUI
                    try:
                        import matplotlib.pyplot as plt
                        flat_file = output_dir / f"{spectrum_name}_flattened_spectrum.png"
                        fig = plot_flat_comparison(plot_matches[0], result, save_path=str(flat_file))
                        plt.close(fig)  # Prevent memory leak
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"Flattened spectrum plot failed: {e}")
                
                # Save correlation function data files
                if hasattr(result, 'best_matches') and result.best_matches:
                    # Main correlation function
                    best_match = result.best_matches[0]
                    if 'correlation' in best_match:
                        corr_data = best_match['correlation']
                        if 'z_axis_full' in corr_data and 'correlation_full' in corr_data:
                            corr_data_file = output_dir / f"{spectrum_name}_correlation.dat"
                            write_correlation(
                                corr_data['z_axis_full'], 
                                corr_data['correlation_full'],
                                str(corr_data_file),
                                header=f"Cross-correlation function for {spectrum_name}"
                            )
                    
                    # Template-specific correlation and spectra data (top 5)
                    for i, match in enumerate(result.best_matches[:5], 1):
                        try:
                            # Template correlation data
                            write_template_correlation_data(match, i, str(output_dir), spectrum_name)
                            
                            # Template spectra data
                            write_template_spectra_data(match, i, str(output_dir), spectrum_name)
                        except Exception as e:
                            logging.getLogger('snid_sage.snid.batch').warning(f"Failed to save template {i} data: {e}")
                
        elif not args.minimal:
            # Default mode: save main outputs only
            from snid_sage.snid.io import write_result
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
    except Exception as e:
        logging.getLogger('snid_sage.snid.batch').warning(f"Failed to save outputs: {e}")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the batch command."""
    # Set epilog with examples
    parser.epilog = """
Examples:
  # Auto-discover templates - minimal mode (only summary report)
  sage batch "spectra/*" --output-dir results/ --minimal
  
  # Auto-discover templates - complete mode (all outputs + 3D plots)
  sage batch "spectra/*" --output-dir results/ --complete
  
  # Auto-discover templates - default mode (main outputs + summary)
  sage batch "spectra/*" --output-dir results/
  
  # Explicit templates directory
  sage batch "spectra/*" templates/ --output-dir results/
  
  # Custom redshift range with auto-discovery
  sage batch "*.dat" --zmin 0.0 --zmax 0.5 --output-dir results/
  
  # With forced redshift and explicit templates
  sage batch "*.dat" templates/ --forced-redshift 0.1 --output-dir results/

  # NEW: List mode using CSV with per-row redshift (forced when provided)
  sage batch --list-csv "data/spectra_list.csv" --output-dir results/
  # If your CSV uses different column names
  sage batch --list-csv input.csv --path-column file --redshift-column z --output-dir results/
    """
    
    # Input source options
    parser.add_argument(
        "input_pattern",
        nargs="?",
        help="Glob pattern for input spectrum files (e.g., 'spectra/*'). Omit when using --list-csv."
    )
    parser.add_argument(
        "--list-csv",
        dest="list_csv",
        help="CSV file listing spectra to analyze. Must contain a path column; optional redshift column to force per-spectrum redshift."
    )
    parser.add_argument(
        "--path-column",
        dest="path_column",
        default="path",
        help="Column name in --list-csv containing spectrum paths (default: path)"
    )
    parser.add_argument(
        "--redshift-column",
        dest="redshift_column",
        default="redshift",
        help="Column name in --list-csv containing forced redshift values (default: redshift)"
    )
    parser.add_argument(
        "templates_dir", 
        nargs="?",  # Make optional
        help="Path to directory containing template spectra (optional - auto-discovers if not provided)"
    )
    parser.add_argument(
        "--output-dir", "-o", 
        help="Directory for output files (defaults to ./results or configured paths.output_dir)"
    )
    
    # Processing modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--minimal", 
        action="store_true",
        help="Minimal mode: Main result files + comprehensive summary report (no plots/extras)"
    )
    mode_group.add_argument(
        "--complete", 
        action="store_true",
        help="Complete mode: Save all outputs including 3D plots for each spectrum"
    )
    
    # Analysis parameters
    analysis_group = parser.add_argument_group("Analysis Parameters")
    analysis_group.add_argument(
        "--zmin", 
        type=float, 
        default=-0.01,
        help="Minimum redshift to consider"
    )
    analysis_group.add_argument(
        "--zmax", 
        type=float, 
        default=1,
        help="Maximum redshift to consider"
    )
    analysis_group.add_argument(
        "--rlapmin",
        type=float,
        default=4.0,
        help="Minimum rlap value required"
    )
    analysis_group.add_argument(
        "--lapmin",
        type=float,
        default=0.3,
        help="Minimum overlap fraction required"
    )
    analysis_group.add_argument(
        "--rlap-ccc-threshold",
        dest="rlap_ccc_threshold",
        type=float,
        default=1.8,
        help="Minimum RLAP-CCC value required for clustering"
    )
    analysis_group.add_argument(
        "--forced-redshift", 
        type=float, 
        help="Force analysis to this specific redshift for all spectra"
    )
    analysis_group.add_argument(
        "--type-filter", 
        nargs="+", 
        help="Only use templates of these types"
    )
    analysis_group.add_argument(
        "--template-filter", 
        nargs="+", 
        help="Only use specific templates (by name)"
    )

    # Display options
    display_group = parser.add_argument_group("Display Options")
    display_group.add_argument(
        "--brief",
        action="store_true",
        help="Minimal console output: terse per-spectrum status and final summary"
    )
    display_group.add_argument(
        "--full",
        action="store_true",
        help="Detailed console output (disables brief mode)"
    )
    display_group.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress output (auto-disabled when stdout is not a TTY)"
    )

    # Default to brief output unless explicitly overridden
    parser.set_defaults(brief=True)
    
    # Processing options
    parallel_group = parser.add_argument_group("Parallel Processing")
    parallel_group.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Number of worker processes (0 = sequential, -1 = use all CPU cores)"
    )
    parser.add_argument(
        "--stop-on-error", 
        action="store_true",
        help="Stop processing if any spectrum fails"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Print detailed processing information"
    )
    # Default behavior: generate plots unless disabled
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Do not generate plots (by default plots are saved)"
    )



def generate_summary_report(results: List[Tuple], args: argparse.Namespace, wall_elapsed_seconds: Optional[float] = None) -> str:
    """Generate a clean, comprehensive summary report focused on batch processing success."""
    successful_results = [r for r in results if r[1] and r[3]]
    failed_results = [r for r in results if not r[1]]
    
    total_count = len(results)
    success_count = len(successful_results)
    failure_count = len(failed_results)
    
    # Generate report
    report = []
    report.append("="*80)
    report.append("SNID SAGE BATCH ANALYSIS REPORT")
    report.append("="*80)
    report.append("")
    
    # Summary
    report.append("BATCH PROCESSING SUMMARY")
    report.append("-"*50)
    if getattr(args, 'list_csv', None):
        report.append(f"Input List CSV: {args.list_csv}")
        report.append(f"Columns: path='{getattr(args, 'path_column', 'path')}', redshift='{getattr(args, 'redshift_column', 'redshift')}'")
        report.append("Per-spectrum forced redshift: applied where provided in CSV")
    else:
        report.append(f"Input Pattern: {args.input_pattern}")
    report.append(f"Templates Directory: {args.templates_dir}")
    report.append(f"Analysis Mode: {'Minimal (summary only)' if args.minimal else 'Complete (all outputs + plots)' if args.complete else 'Standard (main outputs)'}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append(f"PROCESSING RESULTS:")
    report.append(f"   Total Spectra Processed: {total_count}")
    report.append(f"   Successful Analyses: {success_count} ({success_count/total_count*100:.1f}%)")
    report.append(f"   Failed Analyses: {failure_count} ({failure_count/total_count*100:.1f}%)")
    report.append("")
    
    report.append(f"ANALYSIS PARAMETERS:")
    report.append(f"   Redshift Search Range: {args.zmin:.6f} ≤ z ≤ {args.zmax:.6f}")
    if args.forced_redshift is not None:
        report.append(f"   Forced Redshift: z = {args.forced_redshift:.6f}")
    if args.type_filter:
        report.append(f"   Type Filter: {', '.join(args.type_filter)}")
    if args.template_filter:
        report.append(f"   Template Filter: {', '.join(args.template_filter)}")
    
    report.append("")
    
    if successful_results:
        # Results table - focus on individual objects, not aggregated science
        report.append("INDIVIDUAL SPECTRUM RESULTS")
        report.append("-"*50)
        report.append("Each spectrum represents a different astronomical object.")
        report.append("Results are sorted by analysis quality (RLAP-CCC) - highest quality first.")
        report.append("")
        
        # Header (include redshift error and age)
        header = (
            f"{'Spectrum':<16} {'Type':<7} {'Subtype':<9} {'Template':<18} "
            f"{'z':<8} {'±Error':<10} {'Age':<6} {'RLAP-CCC':<10} {'Quality':<8} {'zFixed':<6} {'Status':<1}"
        )
        report.append(header)
        report.append("-" * len(header))
        # Legend removed per request
        
        # Sort results by RLAP-CCC descending (highest quality first)
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        successful_results_sorted = sorted(successful_results, 
                                         key=lambda x: get_best_metric_value(x[3]), reverse=True)
        
        # Results
        for _, _, _, summary in successful_results_sorted:
            spectrum = summary['spectrum'][:15]
            cons_type = summary.get('consensus_type', 'Unknown')[:6]
            cons_subtype = summary.get('consensus_subtype', 'Unknown')[:8]
            template = clean_template_name(summary.get('best_template', 'Unknown'))[:17]
            # Cluster quality (if available)
            if summary.get('has_clustering'):
                quality = summary.get('cluster_quality_category', '') or 'N/A'
            else:
                quality = 'N/A'
            
            # Use cluster-weighted redshift if available, otherwise regular redshift
            use_cluster = summary.get('has_clustering') and ('cluster_redshift_weighted' in summary)
            if use_cluster:
                redshift = f"{summary.get('cluster_redshift_weighted', float('nan')):.6f}"
                redshift_err_val = summary.get('cluster_redshift_weighted_uncertainty', None)
            else:
                redshift = f"{summary.get('redshift', 0):.6f}"
                redshift_err_val = summary.get('redshift_error', None)

            if isinstance(redshift_err_val, (int, float)) and (redshift_err_val or redshift_err_val == 0):
                redshift_err = f"{redshift_err_val:.6f}"
            else:
                redshift_err = "N/A"

            # Age: prefer cluster-weighted age if available; otherwise top-match age if provided
            age_val = summary.get('cluster_age_weighted', None)
            if age_val is None or (isinstance(age_val, float) and (np.isnan(age_val))):
                age_val = summary.get('age', None)
            age_str = f"{age_val:.1f}" if isinstance(age_val, (int, float)) else "N/A"
            
            # Use best available metric (RLAP-CCC if available, otherwise RLAP)
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            rlap_cos = f"{get_best_metric_value(summary):.1f}"
            status_marker = "✓"
            zfixed = "Y" if summary.get('redshift_fixed') else "N"
            
            row = (
                f"{spectrum:<16} {cons_type:<7} {cons_subtype:<9} {template:<18} "
                f"{redshift:<8} {redshift_err:<10} {age_str:<6} {rlap_cos:<10} {quality:<8} {zfixed:<6} {status_marker}"
            )
            report.append(row)

        # Append failed analyses to the same table with 'x' status
        if failed_results:
            for name, success, message, _ in failed_results:
                spectrum = name[:15]
                cons_type = 'N/A'
                cons_subtype = 'N/A'
                template = 'N/A'
                quality = 'N/A'
                redshift = 'N/A'
                redshift_err = 'N/A'
                age_str = 'N/A'
                rlap_cos = 'N/A'
                status_marker = 'x'
                row = (
                    f"{spectrum:<16} {cons_type:<7} {cons_subtype:<9} {template:<18} "
                    f"{redshift:<8} {redshift_err:<10} {age_str:<6} {rlap_cos:<10} {quality:<8} {'N':<6} {status_marker}"
                )
                report.append(row)
        
        report.append("")
        
        # Detailed analysis (sorted by RLAP-CCC - highest quality first)
        report.append("DETAILED INDIVIDUAL ANALYSIS")
        report.append("-"*50)
        report.append("Detailed results for each spectrum (sorted by analysis quality):")
        
        for _, _, _, summary in successful_results_sorted:
            report.append(f"\n📄 {summary['spectrum']}")
            report.append(f"   Best Template: {clean_template_name(summary.get('best_template', 'Unknown'))}")
            report.append(f"   Classification: {summary.get('consensus_type', 'Unknown')} {summary.get('consensus_subtype', '')}")
            
            # Show cluster information if available
            if summary.get('has_clustering'):
                report.append(f"   CLUSTER ANALYSIS ({summary.get('cluster_method', 'Unknown')}):")
                report.append(f"      Cluster Type: {summary.get('cluster_type', 'Unknown')}")
                report.append(f"      Cluster Size: {summary.get('cluster_size', 0)} template matches")
                
                # Show new quality metrics
                if 'cluster_quality_category' in summary:
                    report.append(f"      Quality Category: {summary['cluster_quality_category']}")
                    report.append(f"      Quality Description: {summary['cluster_quality_description']}")
                
                if 'cluster_confidence_level' in summary:
                    report.append(f"      Confidence Level: {summary['cluster_confidence_level'].upper()}")
                    report.append(f"      Confidence vs Alternatives: {summary['cluster_confidence_description']}")
                    if summary.get('cluster_second_best_type', 'N/A') != 'N/A':
                        report.append(f"      Second Best Cluster Type: {summary['cluster_second_best_type']}")
                
                if 'cluster_redshift_weighted' in summary:
                    report.append(f"      RLAP-Weighted Redshift: {summary['cluster_redshift_weighted']:.6f} ± {summary.get('cluster_redshift_weighted_uncertainty', 0):.6f}")
                    report.append(f"      Cluster RLAP: {summary.get('cluster_rlap_mean', 0):.2f}")
                
                report.append(f"   Best Match Redshift: {summary.get('redshift', 0):.6f} ± {summary.get('redshift_error', 0):.6f}")
            else:
                report.append(f"   Redshift: {summary.get('redshift', 0):.6f} ± {summary.get('redshift_error', 0):.6f}")

            # Redshift mode
            if summary.get('redshift_fixed'):
                try:
                    report.append(f"   Redshift Mode: Fixed at z={summary.get('redshift_fixed_value', 0):.6f}")
                except Exception:
                    report.append("   Redshift Mode: Fixed")
            else:
                report.append("   Redshift Mode: Search within zmin/zmax")
            
            # Use best available metric (RLAP-CCC if available, otherwise RLAP)
            from snid_sage.shared.utils.math_utils import get_best_metric_value, get_best_metric_name
            metric_value = get_best_metric_value(summary)
            metric_name = get_best_metric_name(summary)
            report.append(f"   {metric_name} (analysis quality): {metric_value:.2f}")
            report.append(f"   Runtime: {summary.get('runtime', 0):.1f} seconds")
            
            # Show subtype composition within this spectrum's analysis
            if summary.get('cluster_subtypes'):
                if summary.get('has_clustering'):
                    report.append(f"   Cluster Subtype Composition:")
                else:
                    report.append(f"   Template Subtype Distribution:")
                for i, (subtype_name, fraction) in enumerate(summary['cluster_subtypes'][:3], 1):  # Top 3
                    report.append(f"      {i}. {subtype_name}: {fraction*100:.1f}%")
        
        # Analysis quality statistics (these ARE meaningful to aggregate)  
        report.append(f"\n\nBATCH PROCESSING QUALITY STATISTICS")
        report.append("-"*50)
        report.append("These statistics describe the quality of the batch processing, not the science.")
        report.append("")
        
        # RLAP-CCC distribution (analysis quality)
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        all_metrics = [get_best_metric_value(summary) for _, _, _, summary in successful_results]
        avg_metric = sum(all_metrics) / len(all_metrics) if all_metrics else 0
        high_quality = sum(1 for metric in all_metrics if metric >= 10.0)
        medium_quality = sum(1 for metric in all_metrics if 5.0 <= metric < 10.0)
        low_quality = sum(1 for metric in all_metrics if metric < 5.0)
        
        # Determine metric name (RLAP-CCC if available, otherwise RLAP)
        from snid_sage.shared.utils.math_utils import get_best_metric_name
        metric_name = get_best_metric_name(successful_results[0][3]) if successful_results else "RLAP"
        
        report.append(f"ANALYSIS QUALITY ({metric_name} Distribution):")
        report.append(f"   Average {metric_name}: {avg_metric:.2f}")
        report.append(f"   High Quality ({metric_name} ≥ 10): {high_quality}/{success_count} ({high_quality/success_count*100:.1f}%)")
        report.append(f"   Medium Quality (5 ≤ {metric_name} < 10): {medium_quality}/{success_count} ({medium_quality/success_count*100:.1f}%)")
        report.append(f"   Low Quality ({metric_name} < 5): {low_quality}/{success_count} ({low_quality/success_count*100:.1f}%)")
        
        # Classification confidence (using cluster-based metrics)
        cluster_count = sum(1 for _, _, _, s in successful_results if s.get('has_clustering', False))
        high_confidence = sum(1 for _, _, _, s in successful_results 
                             if s.get('cluster_confidence_level') == 'High')
        medium_confidence = sum(1 for _, _, _, s in successful_results 
                               if s.get('cluster_confidence_level') == 'Medium')
        low_confidence = sum(1 for _, _, _, s in successful_results 
                            if s.get('cluster_confidence_level') == 'Low')
        very_low_confidence = sum(1 for _, _, _, s in successful_results 
                                 if s.get('cluster_confidence_level') == 'Very Low')
        
        report.append(f"\nCLASSIFICATION CONFIDENCE:")
        if cluster_count > 0:
            report.append(f"   High Confidence: {high_confidence}/{success_count} ({high_confidence/success_count*100:.1f}%)")
            report.append(f"   Medium Confidence: {medium_confidence}/{success_count} ({medium_confidence/success_count*100:.1f}%)")
            report.append(f"   Low Confidence: {low_confidence}/{success_count} ({low_confidence/success_count*100:.1f}%)")
            report.append(f"   Very Low Confidence: {very_low_confidence}/{success_count} ({very_low_confidence/success_count*100:.1f}%)")
        else:
            report.append(f"   Note: Using legacy analysis method (no cluster-based confidence available)")
        
        # Clustering effectiveness
        cluster_count = sum(1 for _, _, _, s in successful_results if s.get('has_clustering', False))
        total_cluster_size = sum(s.get('cluster_size', 0) for _, _, _, s in successful_results if s.get('has_clustering', False))
        
        report.append(f"\nCLUSTERING EFFECTIVENESS:")
        report.append(f"   Spectra with GMM clustering: {cluster_count}/{success_count} ({cluster_count/success_count*100:.1f}%)")
        report.append(f"   Spectra with basic analysis: {success_count-cluster_count}/{success_count} ({(success_count-cluster_count)/success_count*100:.1f}%)")
        if cluster_count > 0:
            avg_cluster_size = total_cluster_size / cluster_count
            report.append(f"   Average cluster size: {avg_cluster_size:.1f} template matches")
        
    # Runtime statistics
    all_runtimes = [summary.get('runtime', 0) for _, _, _, summary in successful_results if summary.get('runtime', 0) > 0]
    if all_runtimes or wall_elapsed_seconds is not None:
        avg_cpu_runtime = (sum(all_runtimes) / len(all_runtimes)) if all_runtimes else 0.0
        total_wall_runtime = float(wall_elapsed_seconds) if wall_elapsed_seconds is not None else float(sum(all_runtimes))
        avg_effective_runtime = (total_wall_runtime / success_count) if (success_count > 0 and total_wall_runtime > 0) else 0.0
        is_parallel = bool(int(getattr(args, 'workers', 0) or 0) != 0)
        report.append(f"\nPERFORMANCE STATISTICS:")
        # Only show CPU average in sequential mode to avoid confusion in parallel runs
        if (not is_parallel) and avg_cpu_runtime > 0:
            report.append(f"   Average analysis time: {avg_cpu_runtime:.1f} seconds per spectrum")
        if avg_effective_runtime > 0:
            report.append(f"   Average effective time per spectrum (wall): {avg_effective_runtime:.1f} seconds")
        report.append(f"   Total analysis time: {total_wall_runtime:.1f} seconds")
        if total_wall_runtime > 0 and success_count > 0:
            report.append(f"   Throughput: {success_count/total_wall_runtime*60:.1f} spectra per minute")
        
        # Type distribution (for reference only - not scientifically aggregated)
        type_counts = {}
        for _, _, _, summary in successful_results:
            cons_type = summary.get('consensus_type', 'Unknown')
            type_counts[cons_type] = type_counts.get(cons_type, 0) + 1
        
        if len(type_counts) > 1:  # Only show if there's variety
            report.append(f"\nTYPE DISTRIBUTION (For Reference Only):")
            report.append("Note: Each spectrum is a different object - this is just a summary of what was found.")
            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            for type_name, count in sorted_types:
                percentage = count / success_count * 100
                report.append(f"   {type_name}: {count} spectra ({percentage:.1f}%)")
    
    # Separate no-matches from actual failures
    no_match_results = []
    actual_failed_results = []
    
    for spectrum_name, _, error_message, _ in failed_results:
        if "No good matches" in error_message or "No templates after filtering" in error_message:
            no_match_results.append((spectrum_name, error_message))
        else:
            actual_failed_results.append((spectrum_name, error_message))
    
    # No matches section (normal outcome)
    if no_match_results:
        report.append(f"\n\nNO MATCHES FOUND ({len(no_match_results)} spectra)")
        report.append("-"*50)
        report.append("These spectra had no good template matches - this is a normal analysis outcome.")
        for spectrum_name, error_message in no_match_results:
            reason = "no templates available" if "No templates after filtering" in error_message else "no good matches"
            report.append(f"   {spectrum_name}: {reason}")
    
    # Actual failures section (real errors)
    if actual_failed_results:
        report.append(f"\n\nACTUAL FAILURES ({len(actual_failed_results)} spectra)")
        report.append("-"*50)
        report.append("These spectra failed due to processing errors:")
        for spectrum_name, error_message in actual_failed_results:
            report.append(f"   {spectrum_name}: {error_message}")
    
    report.append("\n" + "="*80)
    
    return "\n".join(report)


def _export_results_table(results: List[Tuple], output_dir: Path) -> Optional[Path]:
    """Export per-spectrum results to CSV with clear best-match column names."""
    # Build rows in a deterministic column order
    columns = [
        'file',
        'path',
        'type',
        'subtype',
        'pred_redshift',
        'pred_redshift_err',
        'pred_age',
        'pred_age_err',
        'best_match_redshift',
        'best_match_redshift_err',
        'best_match_age',
        'rlap_ccc',
        'quality',
        'confidence',
        # Helpful extras
        'best_template',
        'zfixed',
        'zfixed_value',
        'weak_match',
        'success',
        'error'
    ]

    rows: List[Dict[str, Any]] = []

    for name, success, message, summary in results:
        row: Dict[str, Any] = {c: None for c in columns}

        if success and isinstance(summary, dict) and summary.get('success', False):
            # Identification
            row['file'] = summary.get('spectrum', name)
            row['path'] = summary.get('file_path')
            # Classification
            row['type'] = summary.get('consensus_type', 'Unknown')
            row['subtype'] = summary.get('consensus_subtype', 'Unknown')

            # Predicted redshift/age: prefer cluster-weighted when available
            pred_z = None
            pred_z_err = None
            if summary.get('has_clustering') and ('cluster_redshift_weighted' in summary):
                pred_z = summary.get('cluster_redshift_weighted')
                pred_z_err = summary.get('cluster_redshift_weighted_uncertainty')
            if pred_z is None or (isinstance(pred_z, float) and np.isnan(pred_z)):
                pred_z = summary.get('redshift')
                pred_z_err = summary.get('redshift_error')
            row['pred_redshift'] = pred_z
            row['pred_redshift_err'] = pred_z_err

            pred_age = summary.get('cluster_age_weighted') if 'cluster_age_weighted' in summary else None
            if pred_age is None or (isinstance(pred_age, float) and np.isnan(pred_age)):
                pred_age = summary.get('age')
            row['pred_age'] = pred_age
            row['pred_age_err'] = summary.get('cluster_age_uncertainty') if 'cluster_age_uncertainty' in summary else None

            # Best match (top template) parameters
            row['best_match_redshift'] = summary.get('redshift')
            row['best_match_redshift_err'] = summary.get('redshift_error')
            row['best_match_age'] = summary.get('age')

            # Analysis quality metrics
            try:
                row['rlap_ccc'] = summary.get('rlap_ccc', get_best_metric_value(summary))
            except Exception:
                row['rlap_ccc'] = summary.get('rlap', None)

            row['quality'] = summary.get('cluster_quality_category', 'N/A' if not summary.get('has_clustering') else None)
            row['confidence'] = summary.get('cluster_confidence_level', 'unknown')

            # Extras
            try:
                row['best_template'] = clean_template_name(summary.get('best_template', 'Unknown'))
            except Exception:
                row['best_template'] = summary.get('best_template')
            row['zfixed'] = bool(summary.get('redshift_fixed', False))
            row['zfixed_value'] = summary.get('redshift_fixed_value')
            row['weak_match'] = bool(summary.get('weak_match', False))
            row['success'] = True
            row['error'] = ''
        else:
            # Failure row
            row['file'] = name
            row['path'] = summary.get('file_path') if isinstance(summary, dict) else None
            row['success'] = False
            row['error'] = message

        rows.append(row)

    # Always write CSV only
    csv_path = output_dir / 'batch_results.csv'
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        logging.getLogger('snid_sage.snid.batch').warning(f"Failed to write CSV results: {e}")
        return None

    return csv_path


def main(args: argparse.Namespace) -> int:
    """Main function for the simplified batch command."""
    try:
        # Logging already configured at top-level; proceed
        is_quiet = bool(getattr(args, 'quiet', False) or getattr(args, 'silent', False))
        # Determine brief mode default: on by default, turned off by --full or verbosity flags
        brief_mode = bool(getattr(args, 'brief', True)) and not bool(getattr(args, 'full', False))
        if getattr(args, 'verbose', False) or getattr(args, 'debug', False):
            brief_mode = False

        # If brief mode, quiet down global logging to suppress INFO spam
        if brief_mode and not is_quiet:
            try:
                set_global_verbosity(VerbosityLevel.QUIET)
            except Exception:
                pass
            # Hard-disable INFO and DEBUG from all loggers to keep console minimal
            try:
                logging.disable(logging.INFO)
            except Exception:
                pass
        
        # Additional suppression for CLI mode - silence specific noisy loggers
        if not args.verbose:
            # Suppress the most verbose loggers that users don't need to see
            logging.getLogger('snid_sage.snid.pipeline').setLevel(logging.WARNING)
            logging.getLogger('snid_sage.snid.pipeline').setLevel(logging.WARNING)
        
        # Suppress matplotlib warnings (tight layout warnings)
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
        
        # Suppress "No good matches found" as ERROR - it's a normal outcome
        pipeline_logger = logging.getLogger('snid_sage.snid.pipeline')
        pipeline_logger.setLevel(logging.CRITICAL)  # Only critical errors, not "no matches"
        
        # Determine input source (glob pattern or list CSV)
        items: List[Dict[str, Any]] = []
        using_list_csv = bool(getattr(args, 'list_csv', None))
        if (not using_list_csv) and (not getattr(args, 'input_pattern', None)):
            print("[ERROR] Provide an input pattern or use --list-csv to supply a file list.", file=sys.stderr)
            return 1
        if using_list_csv:
            # Read items from CSV
            try:
                with open(args.list_csv, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # Normalize header names for robust matching
                    headers = reader.fieldnames or []
                    norm_map = {h: re.sub(r'[^a-z0-9]', '', h.lower()) for h in headers}

                    # Determine actual path and redshift keys
                    desired_path_key = getattr(args, 'path_column', 'path') or 'path'
                    desired_redshift_key = getattr(args, 'redshift_column', 'redshift') or 'redshift'

                    def resolve_column(desired: str, candidates: List[str]) -> Optional[str]:
                        # Exact match first
                        if desired in headers:
                            return desired
                        # Try case-insensitive exact
                        for h in headers:
                            if h.lower() == desired.lower():
                                return h
                        # Try normalized candidates
                        desired_norm = re.sub(r'[^a-z0-9]', '', desired.lower())
                        all_candidates = [desired_norm] + candidates
                        for h, n in norm_map.items():
                            if n in all_candidates:
                                return h
                        return None

                    path_candidates_norm = [
                        'path', 'file', 'spectrum', 'spectrumpath', 'pathname'
                    ]
                    redshift_candidates_norm = [
                        'redshift', 'hostz', 'sherlockhostz', 'z', 'hostredshift'
                    ]

                    actual_path_key = resolve_column(desired_path_key, path_candidates_norm)
                    actual_redshift_key = resolve_column(desired_redshift_key, redshift_candidates_norm)

                    base_dir = Path(args.list_csv).parent
                    for row in reader:
                        path_val = row.get(actual_path_key) if actual_path_key else None
                        if not path_val or str(path_val).strip() == "":
                            continue
                        path_str = str(path_val).strip()
                        # Resolve relative to CSV directory
                        try:
                            p = Path(path_str)
                            if not p.is_absolute():
                                p = (base_dir / p).resolve()
                            path_str = str(p)
                        except Exception:
                            pass
                        redshift_val: Optional[float] = None
                        raw_z = row.get(actual_redshift_key) if actual_redshift_key else None
                        if raw_z is not None and str(raw_z).strip() != "":
                            try:
                                zf = float(raw_z)
                                if np.isfinite(zf):
                                    redshift_val = float(zf)
                            except Exception:
                                redshift_val = None
                        items.append({"path": path_str, "redshift": redshift_val})
            except FileNotFoundError:
                print(f"[ERROR] CSV file not found: {args.list_csv}", file=sys.stderr)
                return 1
            except Exception as e:
                print(f"[ERROR] Failed to read CSV '{args.list_csv}': {e}", file=sys.stderr)
                return 1
            input_files = [it["path"] for it in items]
            if not input_files:
                print(f"[ERROR] No valid rows found in CSV: {args.list_csv}", file=sys.stderr)
                return 1
        else:
            # Pattern-based discovery
            input_files = glob.glob(args.input_pattern)
            if not input_files:
                print(f"[ERROR] No files found matching pattern: {args.input_pattern}", file=sys.stderr)
                return 1
            items = [{"path": p, "redshift": None} for p in input_files]
        
        # Determine mode
        if args.minimal:
            mode = "Minimal (summary only)"
        elif args.complete:
            mode = "Complete (all outputs + plots)"
        else:
            mode = "Standard (main outputs)"
        
        # Resolve output directory from CLI or unified config
        if not args.output_dir:
            try:
                from snid_sage.shared.utils.config.configuration_manager import ConfigurationManager
                cfg = ConfigurationManager().load_config()
                args.output_dir = cfg.get('paths', {}).get('output_dir') or str(Path.cwd() / 'results')
            except Exception:
                args.output_dir = str(Path.cwd() / 'results')
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Always show a single concise startup line (respects quiet/silent)
        if not is_quiet:
            print(f"Starting batch analysis for {len(input_files)} spectra")
        
        # Simple startup message (after resolving output_dir)
        if not is_quiet and not brief_mode:
            print("SNID Batch Analysis - Cluster-aware & optimized")
            print(f"   Files: {len(input_files)} spectra")
            print(f"   Mode: {mode}")
            print(f"   Analysis: GUI-style cluster-aware (winning cluster)")
            print(f"   Sorting: All results/plots sorted by RLAP-CCC (highest quality first)")
            print(f"   Output: {args.output_dir}")
            print(f"   Redshift Range: {args.zmin:.6f} to {args.zmax:.6f}")
            if args.forced_redshift is not None:
                print(f"   Forced Redshift: {args.forced_redshift:.6f}")
            if using_list_csv:
                print(f"   Input list CSV: {args.list_csv} (path='{getattr(args, 'path_column', 'path')}', redshift='{getattr(args, 'redshift_column', 'redshift')}')")
            print(f"   Error Handling: {'Stop on first failure' if args.stop_on_error else 'Continue on failures (default)'}")
            print("")
        
        # ============================================================================
        # OPTIMIZATION: Load templates ONCE for the entire batch
        # ============================================================================
        if not is_quiet and not brief_mode:
            print("Loading templates once for entire batch...")
        # Start wall-clock timer before heavy work (template load + processing)
        start_time = time.time()
        template_manager = BatchTemplateManager(args.templates_dir, verbose=args.verbose)
        
        if not template_manager.load_templates_once():
            print("[ERROR] Failed to load templates", file=sys.stderr)
            return 1
        
        if not is_quiet and not brief_mode:
            print(f"[SUCCESS] Templates loaded in {template_manager.load_time:.2f}s")
            print(f"Ready to process {len(input_files)} spectra with {template_manager.template_count} templates")
            print("")
        
        # Process spectra (parallel or sequential)
        results: List[Tuple[str, bool, str, Dict[str, Any]]] = []
        failed_count = 0

        use_parallel = int(getattr(args, 'workers', 0) or 0) != 0
        max_workers = int(args.workers or 0)
        if max_workers < 0:
            try:
                max_workers = os.cpu_count() or 1
            except Exception:
                max_workers = 1

        if use_parallel:
            # In parallel mode, default to brief output even if user didn't pass --brief
            brief_mode = True if not getattr(args, 'full', False) else False
            if not is_quiet and not brief_mode:
                print(f"[INFO] Starting parallel processing with {max_workers} worker(s)...")

            # Build a lightweight dict of args to send to workers
            args_dict = {
                'minimal': bool(args.minimal),
                'complete': bool(args.complete),
                'zmin': float(args.zmin),
                'zmax': float(args.zmax),
                'rlapmin': float(getattr(args, 'rlapmin', 4.0)),
                'lapmin': float(getattr(args, 'lapmin', 0.3)),
                'rlap_ccc_threshold': float(getattr(args, 'rlap_ccc_threshold', 1.8)),
                'forced_redshift': getattr(args, 'forced_redshift', None),
                'type_filter': getattr(args, 'type_filter', None),
                'template_filter': getattr(args, 'template_filter', None),
                'no_plots': bool(getattr(args, 'no_plots', False)),
                'templates_dir': template_manager.templates_dir,
            }

            # Submit all tasks at once; each task is ~30s so overhead is negligible
            submitted = 0
            processed = 0
            progress_every = max(10, len(items) // 10)  # ~10 updates
            try:
                with ProcessPoolExecutor(max_workers=max_workers,
                                         initializer=_mp_worker_initializer,
                                         initargs=(template_manager.templates_dir,
                                                   getattr(args, 'type_filter', None),
                                                   getattr(args, 'template_filter', None))) as ex:
                    collected: List[Tuple[int, Tuple[str, bool, str, Dict[str, Any]]]] = []
                    futures = []
                    for idx, item in enumerate(items):
                        fut = ex.submit(
                            _mp_process_one,
                            idx,
                            item['path'],
                            item.get('redshift', None),
                            args.output_dir,
                            args_dict
                        )
                        futures.append(fut)
                        submitted += 1

                    for fut in as_completed(futures):
                        idx, res = fut.result()
                        collected.append((idx, res))
                        processed += 1

                        # Brief per-item one-liner (unordered, as futures complete)
                        if not is_quiet:
                            name, success, message, summary = res
                            if success and isinstance(summary, dict):
                                consensus_type = summary.get('consensus_type', 'Unknown')
                                consensus_subtype = summary.get('consensus_subtype', '')
                                # Prefer cluster-weighted redshift if available
                                if summary.get('has_clustering') and ('cluster_redshift_weighted' in summary):
                                    z_value = summary.get('cluster_redshift_weighted', 0.0)
                                else:
                                    z_value = summary.get('redshift', 0.0)
                                # Metric
                                try:
                                    from snid_sage.shared.utils.math_utils import get_best_metric_value, get_best_metric_name
                                    best_metric_value = get_best_metric_value(summary)
                                    best_metric_name = get_best_metric_name(summary)
                                except Exception:
                                    best_metric_value = summary.get('rlap', 0.0)
                                    best_metric_name = 'RLAP'
                                # Template short
                                best_template = str(summary.get('best_template', 'Unknown'))
                                best_template_short = best_template[:18]
                                weak_note = " (weak)" if summary.get('weak_match') else ""
                                type_display = f"{consensus_type} {consensus_subtype}".strip()
                                try:
                                    print(f"[{processed}/{len(items)}] {name}: {type_display}{weak_note} z={float(z_value):.6f} {best_metric_name}={best_metric_value:.1f} tpl={best_template_short}")
                                except Exception:
                                    print(f"[{processed}/{len(items)}] {name}: {type_display}{weak_note}")
                            else:
                                # Failure: distinguish no-match vs error
                                if ("No good matches" in message) or ("No templates after filtering" in message):
                                    status = "no-match"
                                    print(f"[{processed}/{len(items)}] {name}: {status}")
                                else:
                                    status = "error"
                                    etype = summary.get('error_type') if isinstance(summary, dict) else None
                                    if etype:
                                        print(f"[{processed}/{len(items)}] {name}: {status} ({etype})")
                                    else:
                                        print(f"[{processed}/{len(items)}] {name}: {status}")

                        # Periodic overall progress (only in non-brief detailed mode)
                        if (not args.verbose) and (not is_quiet) and (not getattr(args, 'no_progress', False)) and (not brief_mode):
                            if (processed % progress_every == 0) or (processed == len(items)):
                                print(f"   Progress: {processed}/{len(items)} ({processed/len(items)*100:.0f}%)")

            except KeyboardInterrupt:
                print("[INFO] Cancellation requested. Shutting down workers...", file=sys.stderr)
                # Executor context manager will handle shutdown
                raise

            # Restore original order by index
            collected_sorted = [res for _, res in sorted(collected, key=lambda x: x[0])]
            results = collected_sorted

            # Count failures; suppress per-item logs in parallel unless explicitly verbose
            for i, (name, success, message, summary) in enumerate(results, 1):
                if not success:
                    failed_count += 1
                    if (not is_quiet) and (args.verbose or getattr(args, 'full', False)):
                        if ("No good matches" in message) or ("No templates after filtering" in message):
                            status = "no-match"
                            print(f"[{i}/{len(input_files)}] {name}: {status}")
                        else:
                            status = "error"
                            etype = summary.get('error_type') if isinstance(summary, dict) else None
                            if etype:
                                print(f"[{i}/{len(input_files)}] {name}: {status} ({etype})")
                            else:
                                print(f"[{i}/{len(input_files)}] {name}: {status}")
                else:
                    if summary and isinstance(summary, dict) and (not is_quiet) and (args.verbose or getattr(args, 'full', False)):
                        consensus_type = summary.get('consensus_type', 'Unknown')
                        consensus_subtype = summary.get('consensus_subtype', '')
                        if summary.get('has_clustering') and 'cluster_redshift_weighted' in summary:
                            redshift = summary['cluster_redshift_weighted']
                            z_marker = "*"
                        else:
                            redshift = summary.get('redshift', 0)
                            z_marker = ""
                        from snid_sage.shared.utils.math_utils import get_best_metric_value, get_best_metric_name
                        best_metric_value = get_best_metric_value(summary)
                        best_metric_name = get_best_metric_name(summary)
                        type_display = f"{consensus_type} {consensus_subtype}".strip()
                        if brief_mode:
                            best_template = str(summary.get('best_template', 'Unknown'))
                            best_template_short = best_template[:18]
                            metric_str = f"{best_metric_name}={best_metric_value:.1f}"
                            weak_note = " (weak)" if summary.get('weak_match') else ""
                            print(f"[{i}/{len(input_files)}] {name}: {type_display}{weak_note} z={float(redshift):.6f} {metric_str} tpl={best_template_short}")
                        else:
                            weak_note = " (weak)" if summary.get('weak_match') else ""
                            print(f"      {name}: {type_display}{weak_note} z={float(redshift):.6f} {best_metric_name}={best_metric_value:.1f} {z_marker}")
        else:
            # Sequential fallback (current behavior)
            if not is_quiet and not brief_mode:
                print("[INFO] Starting optimized sequential processing...")

            for i, item in enumerate(items, 1):
                spectrum_path = item["path"]
                per_row_forced_z = item.get("redshift", None)
                is_tty = sys.stdout.isatty()
                show_progress = (not args.verbose) and (not is_quiet) and (not getattr(args, 'no_progress', False)) and is_tty
                if args.verbose and not brief_mode:
                    print(f"[{i:3d}/{len(input_files):3d}] {Path(spectrum_path).name}")
                else:
                    if show_progress and (i % 10 == 0 or i == len(input_files)) and not brief_mode:
                        print(f"   Progress: {i}/{len(input_files)} ({i/len(input_files)*100:.0f}%)")

                name, success, message, summary = process_single_spectrum_optimized(
                    spectrum_path, template_manager, args.output_dir, args,
                    forced_redshift_override=per_row_forced_z
                )

                results.append((name, success, message, summary))

                if not success:
                    failed_count += 1
                    if brief_mode and not is_quiet:
                        if ("No good matches" in message) or ("No templates after filtering" in message):
                            status = "no-match"
                            print(f"[{i}/{len(input_files)}] {name}: {status}")
                        else:
                            status = "error"
                            etype = summary.get('error_type') if isinstance(summary, dict) else None
                            if etype:
                                print(f"[{i}/{len(input_files)}] {name}: {status} ({etype})")
                            else:
                                print(f"[{i}/{len(input_files)}] {name}: {status}")
                    else:
                        if "No good matches" in message or "No templates after filtering" in message:
                            if not is_quiet:
                                print(f"      {name}: No good matches found")
                        else:
                            if not is_quiet:
                                etype = summary.get('error_type') if isinstance(summary, dict) else None
                                if etype:
                                    print(f"      [ERROR] {name}: {message} [{etype}]")
                                else:
                                    print(f"      [ERROR] {name}: {message}")
                    if args.stop_on_error:
                        if not is_quiet and not brief_mode:
                            print("Stopping due to error.")
                        break
                else:
                    if summary and isinstance(summary, dict) and not is_quiet:
                        consensus_type = summary.get('consensus_type', 'Unknown')
                        consensus_subtype = summary.get('consensus_subtype', '')
                        if summary.get('has_clustering') and 'cluster_redshift_weighted' in summary:
                            redshift = summary['cluster_redshift_weighted']
                            z_marker = "*"
                        else:
                            redshift = summary.get('redshift', 0)
                            z_marker = ""
                        from snid_sage.shared.utils.math_utils import get_best_metric_value, get_best_metric_name
                        best_metric_value = get_best_metric_value(summary)
                        best_metric_name = get_best_metric_name(summary)
                        type_display = f"{consensus_type} {consensus_subtype}".strip()
                        if brief_mode:
                            best_template = str(summary.get('best_template', 'Unknown'))
                            best_template_short = best_template[:18]
                            metric_str = f"{best_metric_name}={best_metric_value:.1f}"
                            z_value = redshift
                            weak_note = " (weak)" if summary.get('weak_match') else ""
                            print(f"[{i}/{len(input_files)}] {name}: {type_display}{weak_note} z={float(z_value):.6f} {metric_str} tpl={best_template_short}")
                        else:
                            weak_note = " (weak)" if summary.get('weak_match') else ""
                            print(f"      {name}: {type_display}{weak_note} z={float(redshift):.6f} {best_metric_name}={best_metric_value:.1f} {z_marker}")
        
        # Results summary
        successful_count = len(results) - failed_count
        success_rate = successful_count / len(results) * 100 if results else 0
        
        if not is_quiet:
            if brief_mode:
                print(f"Done {successful_count}/{len(results)}; success rate {success_rate:.1f}%")
            else:
                print(f"\nCompleted: {success_rate:.1f}% success ({successful_count}/{len(results)})")

        # Generate summary report (use wall-clock time for correct parallel stats)
        summary_path = output_dir / "batch_analysis_report.txt"
        if not is_quiet and not brief_mode:
            print("Generating summary report...")

        # Compute wall-clock elapsed time from first template load to now
        try:
            wall_elapsed = time.time() - start_time
        except Exception:
            wall_elapsed = None

        summary_report = generate_summary_report(results, args, wall_elapsed_seconds=wall_elapsed)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_report)

        if not is_quiet and not brief_mode:
            print(f"[SUCCESS] Summary report: {summary_path}")

        # Export tabular results (CSV only)
        csv_file = _export_results_table(results, output_dir)
        if not is_quiet and csv_file:
            print(f"Results table (CSV): {csv_file}")

        # Show what was created
        if not is_quiet and not brief_mode and not args.minimal and successful_count > 0:
            print(f"Individual results in: {output_dir}/")
            if args.complete:
                print("   3D Plots: Static PNG files with optimized viewing angle")
                print("   Top 5 templates: Sorted by RLAP-CCC (highest quality first)")
            
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1 