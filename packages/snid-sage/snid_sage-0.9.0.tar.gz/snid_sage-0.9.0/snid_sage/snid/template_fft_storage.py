"""
Unified Template FFT Storage System - OPTIMIZED VERSION
======================================================

This module provides a unified storage system for pre-computed template FFTs
that replaces the complex caching architecture with a simple, fast approach.

Key Features:
- Templates are rebinned to standard grid during H5 creation (not runtime)
- Single wavelength array stored for all templates (same grid)
- Fast filtering by type, subtype, age without loading data
- Memory-efficient: loads all templates at once with prefetching
- Automatic FFT pre-computation and storage
- Multi-epoch template support

Usage:
    storage = TemplateFFTStorage('/path/to/templates')
    # Storage is expected to be prebuilt (HDF5 + index present)
    templates = storage.get_templates(type_filter=['Ia'], age_range=(0, 50))
"""

import numpy as np
import h5py
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Use centralized logging if available
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOG = get_logger('snid.template_fft_storage')
except ImportError:
    _LOG = logging.getLogger('snid_sage.snid.template_fft_storage')

@dataclass
class TemplateEntry:
    """Template entry with metadata and data (already rebinned to standard grid)"""
    name: str
    type: str
    subtype: str
    age: float
    redshift: float
    phase: str
    flux: np.ndarray  # Already rebinned to standard grid
    fft: np.ndarray   # Pre-computed FFT
    epochs: int = 1
    epoch_data: List[Dict] = None
    file_path: str = ""
    
    def __post_init__(self):
        if self.epoch_data is None:
            self.epoch_data = []


class TemplateFFTStorage:
    """
    Unified storage system for template FFTs and metadata - OPTIMIZED VERSION.
    
    This replaces the complex caching system with a simple approach:
    1. Build unified storage once from template directory WITH REBINNING
    2. Store single wavelength array for all templates (same grid)
    3. Fast metadata-based filtering without loading full data
    4. Load all templates at once with prefetching support
    5. Pre-computed FFTs stored alongside data
    """
    
    def __init__(self, template_dir: str, output_dir: str = None):
        """
        Initialize unified template storage.
        
        Parameters
        ----------
        template_dir : str
            Directory containing template files
        output_dir : str, optional
            Directory to write HDF5 and index files (default: template_dir)
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir) if output_dir else self.template_dir
        self.storage_files = {}  # Will be populated with type -> file mapping
        self.index_file = self.output_dir / 'template_index.json'
        
        # Load index if available
        self._index: Optional[Dict] = None
        self._load_index()
        
        # Standard grid parameters (same as SNID uses)
        self.NW = 1024
        self.W0 = 2500.0
        self.W1 = 10000.0
        self.DWLOG = np.log(self.W1 / self.W0) / self.NW
        
        # Precompute standard wavelength grid
        self.standard_log_wave = self.W0 * np.exp((np.arange(self.NW) + 0.5) * self.DWLOG)
        
        # Prefetching support - LAZY INITIALIZATION (only when needed)
        self._prefetch_executor = None
        self._prefetch_cache = {}
        self._prefetch_lock = threading.Lock()
        
        _LOG.info(f"Initialized TemplateFFTStorage: {template_dir}")
        _LOG.debug(f"Standard grid: NW={self.NW}, W0={self.W0:.1f}, W1={self.W1:.1f}, DWLOG={self.DWLOG:.6f}")
        
    def __del__(self):
        """Clean up thread pool on destruction"""
        if hasattr(self, '_prefetch_executor') and self._prefetch_executor:
            self._prefetch_executor.shutdown(wait=False)
    
    def _ensure_prefetch_executor(self):
        """Lazily initialize prefetch executor only when needed"""
        if self._prefetch_executor is None:
            self._prefetch_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="template_prefetch")
            _LOG.debug("Initialized prefetch executor on demand")
        
    def is_built(self) -> bool:
        """Check if unified storage has been built - FAST startup version."""
        # FAST CHECK: Only check for index file during startup
        return self.index_file.exists() and self._index is not None
    
    def is_fully_built(self) -> bool:
        """Check if unified storage is fully built with all files (slower validation)."""
        if not (self.index_file.exists() and self._index is not None):
            return False
        
        # Check that all expected type files exist, preferring storage_file from index
        expected_types = set(self._index.get('by_type', {}).keys())
        for sn_type in expected_types:
            type_info = (self._index.get('by_type') or {}).get(sn_type) or {}
            storage_path = type_info.get('storage_file')
            if storage_path:
                # Resolve relative to template_dir if needed
                storage_file = Path(storage_path)
                if not storage_file.is_absolute():
                    storage_file = self.template_dir / storage_path
            else:
                storage_file = self._get_storage_file_for_type(sn_type)
            if not storage_file.exists():
                return False
        
        return True
    
    def needs_rebuild(self) -> bool:
        """Rebuild disabled; templates are expected to be prebuilt."""
        return False
    
    def _get_storage_file_for_type(self, sn_type: str) -> Path:
        """Get storage file path for a specific supernova type."""
        safe_type = sn_type.replace('/', '_').replace('-', '_').replace(' ', '_')
        return self.output_dir / f'templates_{safe_type}.hdf5'
    
    def get_available_types(self) -> List[str]:
        """Get list of available supernova types."""
        if not self._index:
            return []
        return list(self._index.get('by_type', {}).keys())
    
    def get_standard_wavelength_grid(self) -> np.ndarray:
        """Get the standard wavelength grid used for all templates."""
        return self.standard_log_wave.copy()
    
    def build_storage(self, force: bool = False) -> None:
        """Rebuild disabled; no action taken."""
        _LOG.info("Unified template storage rebuild is disabled. Ensure HDF5 and index files are provided.")
        return
        
    def get_templates(self, 
                     type_filter: Optional[List[str]] = None,
                     subtype_filter: Optional[List[str]] = None,
                     age_range: Optional[Tuple[float, float]] = None,
                     template_names: Optional[List[str]] = None,
                     use_prefetching: bool = True,
                     progress_callback: Optional[Callable[[str, float], None]] = None) -> List[TemplateEntry]:
        """
        Get templates with fast filtering and optional prefetching.
        
        Parameters
        ----------
        type_filter : List[str], optional
            Types to include (e.g., ['Ia', 'II-P'])
        subtype_filter : List[str], optional
            Subtypes to include
        age_range : Tuple[float, float], optional
            Age range (min_age, max_age)
        template_names : List[str], optional
            Specific template names to load
        use_prefetching : bool, optional
            Whether to use prefetching for better performance
            
        Returns
        -------
        List[TemplateEntry]
            Templates with flux already rebinned to standard grid
        """
        if not self.is_fully_built():
            _LOG.error("Unified storage index/files missing. Ensure prebuilt HDF5 and index exist.")
            return []
        
        # Filter templates by metadata
        candidate_names = self._filter_templates_by_metadata(
            type_filter, subtype_filter, age_range, template_names
        )
        
        if not candidate_names:
            return []
        
        # Notify initial state
        try:
            if progress_callback is not None:
                progress_callback(f"Preparing to load {len(candidate_names)} templates", 0.0)
        except Exception:
            pass

        # Load templates from storage
        if use_prefetching:
            return self._load_templates_with_prefetching(candidate_names, progress_callback)
        else:
            return self._load_templates_from_storage(candidate_names, progress_callback)
    
    def get_template_fft(self, template_name: str) -> Optional[np.ndarray]:
        """
        Get pre-computed FFT for a specific template.
        
        Parameters
        ----------
        template_name : str
            Name of template
            
        Returns
        -------
        np.ndarray or None
            Pre-computed FFT or None if not found
        """
        if not self.is_fully_built():
            return None
        
        try:
            if template_name in self._index['templates']:
                storage_file = self._index['templates'][template_name]['storage_file']
                
                # Resolve storage file path relative to template directory if it's not absolute
                if not Path(storage_file).is_absolute():
                    storage_file = str(self.template_dir / storage_file)
                
                with h5py.File(storage_file, 'r') as f:
                    if f"templates/{template_name}" not in f:
                        return None
                    
                    group = f[f"templates/{template_name}"]
                    fft_real = group['fft_real'][:]
                    fft_imag = group['fft_imag'][:]
                    return fft_real + 1j * fft_imag
                    
        except Exception as e:
            _LOG.error(f"Failed to load FFT for {template_name}: {e}")
            return None
    
    def get_template_metadata(self, template_name: str) -> Optional[Dict]:
        """Get metadata for a template without loading full data."""
        if self._index and template_name in self._index.get('templates', {}):
            return self._index['templates'][template_name].copy()
        return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if not self._index:
            return {}
        
        stats = {
            'total_templates': self._index.get('template_count', 0),
            'types': len(self._index.get('by_type', {})),
            'storage_files': []
        }
        
        for sn_type, type_info in self._index.get('by_type', {}).items():
            storage_file_path = type_info['storage_file']
            # Resolve storage file path relative to template directory if it's not absolute
            if not Path(storage_file_path).is_absolute():
                storage_file_path = str(self.template_dir / storage_file_path)
            storage_file = Path(storage_file_path)
            
            file_stats = {
                'type': sn_type,
                'file': str(storage_file),
                'templates': type_info['count'],
                'exists': storage_file.exists()
            }
            if storage_file.exists():
                file_stats['size_mb'] = storage_file.stat().st_size / (1024 * 1024)
            stats['storage_files'].append(file_stats)
        
        return stats
    
    def _load_index(self):
        """Load the template index file with optional user override support.

        Behavior:
        - Load the base index from `template_index.json` (required for built-in templates)
        - If a user index exists at `User_templates/template_index.user.json`, merge it
          with the following rule:
            • For any type that has a user HDF5 storage file present (templates_<Type>.user.hdf5),
              perform a type-level override: only user templates for that type are used and the
              storage_file points to the user HDF5 file. All built-in templates for that type are
              excluded.
            • For types without a user storage file, keep the built-in index entries as-is.
        This enables per-type user customization while keeping other types from the base library.
        """
        base_index: Optional[Dict[str, Any]] = None
        user_index: Optional[Dict[str, Any]] = None

        # 1) Load base index
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    base_index = json.load(f)
            except Exception as e:
                _LOG.warning(f"Failed to load index file: {e}")
                base_index = None

        # 2) Load user index if present
        user_dir = self.template_dir / 'User_templates'
        user_index_path = user_dir / 'template_index.user.json'
        if user_index_path.exists():
            try:
                with open(user_index_path, 'r', encoding='utf-8') as f:
                    user_index = json.load(f)
            except Exception as e:
                _LOG.warning(f"Failed to load user index file: {e}")
                user_index = None

        # If no base index and no user index, nothing to do
        if base_index is None and user_index is None:
            self._index = None
            return

        # Helper to build safe type filename suffix
        def _safe_type_name(type_name: str) -> str:
            return (
                type_name.replace('/', '_').replace('-', '_').replace(' ', '_')
                if isinstance(type_name, str) else 'Unknown'
            )

        # Start from base index (or an empty structure if missing)
        merged = base_index or {
            'version': '2.0',
            'created_date': None,
            'template_count': 0,
            'grid_rebinned': True,
            'grid_params': {},
            'templates': {},
            'by_type': {}
        }

        # Nothing to merge if no user index
        if not user_index:
            self._index = merged
            return

        # Determine which types have a user storage file present; these types will be overridden
        overridden_types = set()
        for ttype, bucket in (user_index.get('by_type') or {}).items():
            safe = _safe_type_name(ttype)
            user_storage = user_dir / f"templates_{safe}.user.hdf5"
            if user_storage.exists():
                overridden_types.add(ttype)

        if not overridden_types:
            # No user storage present; keep base index and simply add any user templates
            # that reference a user storage file path (best-effort enrich)
            user_templates = user_index.get('templates', {})
            merged_templates = merged.setdefault('templates', {})
            for name, meta in user_templates.items():
                merged_templates[name] = meta
            # Recompute by_type counts conservatively (prefer existing by_type storage_file)
            by_type: Dict[str, Any] = {}
            for name, meta in merged_templates.items():
                ttype = meta.get('type', 'Unknown')
                bucket = by_type.setdefault(ttype, {"count": 0, "storage_file": meta.get("storage_file", ""), "template_names": []})
                bucket['count'] += 1
                bucket['template_names'].append(name)
                if not bucket.get('storage_file') and meta.get('storage_file'):
                    bucket['storage_file'] = meta['storage_file']
            merged['by_type'] = by_type
            merged['template_count'] = len(merged_templates)
            self._index = merged
            return

        # Perform type-level override for types with user storage files
        base_templates = merged.get('templates', {})
        user_templates = user_index.get('templates', {})

        # Remove base templates for overridden types
        names_to_remove = [
            name for name, meta in base_templates.items()
            if meta.get('type') in overridden_types
        ]
        for name in names_to_remove:
            base_templates.pop(name, None)

        # Add user templates for overridden types
        for name, meta in user_templates.items():
            if meta.get('type') in overridden_types:
                # Ensure storage_file points to user path (normalize to forward slashes)
                ttype = meta.get('type', 'Unknown')
                safe = _safe_type_name(ttype)
                meta = dict(meta)
                meta['storage_file'] = str(Path('User_templates') / f"templates_{safe}.user.hdf5").replace('\\', '/')
                base_templates[name] = meta

        # Rebuild by_type with storage_file pointing to user file for overridden types
        new_by_type: Dict[str, Any] = {}
        for name, meta in base_templates.items():
            ttype = meta.get('type', 'Unknown')
            bucket = new_by_type.setdefault(ttype, {"count": 0, "storage_file": meta.get("storage_file", ""), "template_names": []})
            bucket['count'] += 1
            bucket['template_names'].append(name)
            # For overridden types, force storage_file to the user file
            if ttype in overridden_types:
                safe = _safe_type_name(ttype)
                bucket['storage_file'] = str(Path('User_templates') / f"templates_{safe}.user.hdf5").replace('\\', '/')
            else:
                # Otherwise, keep any existing storage_file (first non-empty wins)
                if not bucket.get('storage_file') and meta.get('storage_file'):
                    bucket['storage_file'] = meta['storage_file']

        merged['templates'] = base_templates
        merged['by_type'] = new_by_type
        merged['template_count'] = len(base_templates)
        self._index = merged
    
    def _load_all_templates_with_rebinning(self) -> List[TemplateEntry]:
        """Load all templates from the template directory and rebin them to standard grid."""
        # Legacy import removed: we no longer build storage from .lnw files
        from snid_sage.snid.preprocessing import log_rebin, init_wavelength_grid
        
        templates = []
        # LNW files are no longer supported as a source. Keep empty list.
        template_files = []
        
        _LOG.info(f"Loading and rebinning {len(template_files)} template files...")
        
        # Initialize wavelength grid for rebinning
        init_wavelength_grid(num_points=self.NW, min_wave=self.W0, max_wave=self.W1)
        
        for i, template_file in enumerate(template_files):
            if i % 100 == 0:
                _LOG.info(f"Processing template {i+1}/{len(template_files)}")
            
            try:
                # Load template data
                # No LNW source: skip
                continue
                
                # Extract metadata
                name = template_file.stem
                template_type = template_data.get('type', 'Unknown')
                subtype = template_data.get('subtype', 'Unknown')
                
                # For age, use the first valid age (not -999.0) if available
                age = float(template_data.get('age', 0))
                if 'ages' in template_data and len(template_data['ages']) > 0:
                    # Find first valid age that's not -999.0
                    for epoch_age in template_data['ages']:
                        if abs(epoch_age - (-999.0)) >= 0.1:  # Not -999.0
                            age = float(epoch_age)
                            break
                
                redshift = float(template_data.get('redshift', 0))
                phase = template_data.get('phase', 'Unknown')
                
                # Get spectral data
                wave = template_data.get('wave', np.array([]))
                flux = template_data.get('flux', np.array([]))
                
                if len(wave) == 0 or len(flux) == 0:
                    _LOG.warning(f"Empty template data: {name}")
                    continue
                
                # Handle multi-epoch templates
                epochs = template_data.get('nepoch', 1)
                epoch_data = []
                valid_epochs = 0
                
                if epochs > 1 and 'flux_matrix' in template_data and 'ages' in template_data:
                    # Extract epoch data from flux_matrix and ages arrays
                    flux_matrix = template_data['flux_matrix']
                    ages_array = template_data['ages']
                    
                    for epoch in range(epochs):
                        # Extract age for this epoch  
                        if epoch < len(ages_array):
                            epoch_age = ages_array[epoch]
                        else:
                            epoch_age = age
                        
                        # FILTER OUT EPOCHS WITH -999.0 AGE (these are useless for analysis)
                        if abs(epoch_age - (-999.0)) < 0.1:  # Use small tolerance for float comparison
                            _LOG.debug(f"Skipping epoch {epoch} of template {name} with invalid age {epoch_age}")
                            continue
                        
                        # Extract flux for this epoch
                        if epoch < flux_matrix.shape[0]:
                            epoch_flux = flux_matrix[epoch]
                        else:
                            epoch_flux = flux
                        
                        # Rebin epoch flux to standard grid
                        if not template_data.get('is_log_rebinned', False):
                            _, epoch_rebinned_flux = log_rebin(wave, epoch_flux)
                        else:
                            if len(epoch_flux) == self.NW:
                                epoch_rebinned_flux = epoch_flux
                            else:
                                # Re-rebin from linear
                                if hasattr(template_data, 'wave_linear'):
                                    wave_linear = template_data['wave_linear']
                                else:
                                    wave_linear = 10.0**np.clip(wave, -20, 20)
                                _, epoch_rebinned_flux = log_rebin(wave_linear, epoch_flux)
                        
                        epoch_info = {
                            'flux': epoch_rebinned_flux,  # Already rebinned
                            'age': epoch_age,
                            'fft': np.fft.fft(epoch_rebinned_flux)
                        }
                        epoch_data.append(epoch_info)
                        valid_epochs += 1
                    
                    # Update epochs count to reflect valid epochs only
                    epochs = valid_epochs
                    if epochs == 0:
                        _LOG.warning(f"Template {name} has no valid epochs (all have -999.0 age), skipping template.")
                        continue  # SKIP THIS TEMPLATE COMPLETELY
                else:
                    # Single-epoch template: check if age is -999.0
                    if 'ages' in template_data and len(template_data['ages']) > 0:
                        if abs(template_data['ages'][0] - (-999.0)) < 0.1:
                            _LOG.warning(f"Template {name} has single epoch with -999.0 age, skipping template.")
                            continue  # SKIP THIS TEMPLATE COMPLETELY
                    elif abs(age - (-999.0)) < 0.1:
                        _LOG.warning(f"Template {name} has single epoch with -999.0 age, skipping template.")
                        continue  # SKIP THIS TEMPLATE COMPLETELY
                
                # Pre-compute FFT on rebinned data
                fft = np.fft.fft(flux)
                
                # Create template entry with rebinned data
                template_entry = TemplateEntry(
                    name=name,
                    type=template_type,
                    subtype=subtype,
                    age=age,
                    redshift=redshift,
                    phase=phase,
                    flux=flux,  # Already rebinned to standard grid
                    fft=fft,
                    epochs=epochs,
                    epoch_data=epoch_data,
                    file_path=str(template_file)
                )
                
                templates.append(template_entry)
                
            except Exception as e:
                _LOG.error(f"Failed to load template {template_file}: {e}")
                continue
        
        _LOG.info(f"Successfully loaded and rebinned {len(templates)} templates")
        return templates
    
    def _build_hdf5_storage_for_type(self, sn_type: str, templates: List[TemplateEntry]):
        """Build HDF5 storage file for a specific supernova type with rebinned data."""
        storage_file = self._get_storage_file_for_type(sn_type)
        
        # Remove existing file
        if storage_file.exists():
            storage_file.unlink()
        
        with h5py.File(storage_file, 'w') as f:
            # Create metadata group
            meta_group = f.create_group('metadata')
            meta_group.attrs['version'] = '2.0'  # Increment version for rebinned data
            meta_group.attrs['created_date'] = time.time()
            meta_group.attrs['template_count'] = len(templates)
            meta_group.attrs['supernova_type'] = sn_type
            meta_group.attrs['grid_rebinned'] = True  # Flag indicating templates are rebinned
            meta_group.attrs['NW'] = self.NW
            meta_group.attrs['W0'] = self.W0
            meta_group.attrs['W1'] = self.W1
            meta_group.attrs['DWLOG'] = self.DWLOG
            
            # Store single wavelength array for all templates (they're all on same grid now)
            meta_group.create_dataset('standard_wavelength', data=self.standard_log_wave)
            
            # Create templates group
            templates_group = f.create_group('templates')
            
            for template in templates:
                # Create group for this template
                template_group = templates_group.create_group(template.name)
                
                # Store rebinned flux (no need to store wavelength - it's in metadata)
                template_group.create_dataset('flux', data=template.flux)
                
                # Store FFT (split into real/imaginary for HDF5 compatibility)
                template_group.create_dataset('fft_real', data=template.fft.real)
                template_group.create_dataset('fft_imag', data=template.fft.imag)
                
                # Store metadata as attributes
                template_group.attrs['type'] = template.type
                template_group.attrs['subtype'] = template.subtype
                template_group.attrs['age'] = template.age
                template_group.attrs['redshift'] = template.redshift
                template_group.attrs['phase'] = template.phase
                template_group.attrs['epochs'] = template.epochs
                template_group.attrs['file_path'] = template.file_path
                template_group.attrs['rebinned'] = True  # Flag for rebinned data
                
                # Store epoch data if multi-epoch
                if template.epochs > 1 and template.epoch_data:
                    epochs_group = template_group.create_group('epochs')
                    for i, epoch_data in enumerate(template.epoch_data):
                        epoch_group = epochs_group.create_group(f'epoch_{i}')
                        epoch_group.create_dataset('flux', data=epoch_data['flux'])
                        epoch_group.create_dataset('fft_real', data=epoch_data['fft'].real)
                        epoch_group.create_dataset('fft_imag', data=epoch_data['fft'].imag)
                        epoch_group.attrs['age'] = epoch_data['age']
                        epoch_group.attrs['rebinned'] = True
        
        _LOG.info(f"Built Type {sn_type} HDF5 storage: {storage_file}")
    
    def _build_index(self, templates_by_type: Dict[str, List[TemplateEntry]]):
        """Build fast lookup index."""
        _LOG.info("Building template index...")
        
        # Count total templates
        total_templates = sum(len(templates) for templates in templates_by_type.values())
        
        index = {
            'version': '2.0',  # Increment version for rebinned data
            'created_date': time.time(),
            'template_count': total_templates,
            'grid_rebinned': True,
            'grid_params': {
                'NW': self.NW,
                'W0': self.W0,
                'W1': self.W1,
                'DWLOG': self.DWLOG
            },
            'templates': {},
            'by_type': {}
        }
        
        # Build templates index and by_type mapping
        for sn_type, templates in templates_by_type.items():
            type_info = {
                'count': len(templates),
                'storage_file': str(self._get_storage_file_for_type(sn_type)),
                'template_names': []
            }
            
            for template in templates:
                index['templates'][template.name] = {
                    'type': template.type,
                    'subtype': template.subtype,
                    'age': template.age,
                    'redshift': template.redshift,
                    'phase': template.phase,
                    'epochs': template.epochs,
                    'file_path': template.file_path,
                    'storage_file': str(self._get_storage_file_for_type(sn_type)),
                    'rebinned': True
                }
                type_info['template_names'].append(template.name)
            
            index['by_type'][sn_type] = type_info
        
        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        self._index = index
        _LOG.info(f"Built template index: {self.index_file} ({len(templates_by_type)} types, {total_templates} templates)")
    
    def _filter_templates_by_metadata(self, 
                                    type_filter: Optional[List[str]],
                                    subtype_filter: Optional[List[str]], 
                                    age_range: Optional[Tuple[float, float]],
                                    template_names: Optional[List[str]]) -> List[str]:
        """Fast filtering using metadata index."""
        if not self._index:
            return []
        
        templates = self._index.get('templates', {})
        candidates = []
        
        for name, metadata in templates.items():
            # Filter by specific names
            if template_names and name not in template_names:
                continue
            
            # Filter by type
            if type_filter and metadata.get('type') not in type_filter:
                continue
            
            # Filter by subtype
            if subtype_filter and metadata.get('subtype') not in subtype_filter:
                continue
            
            # Filter by age range
            if age_range:
                age = metadata.get('age', 0)
                if age < age_range[0] or age > age_range[1]:
                    continue
            
            candidates.append(name)
        
        return candidates
    
    def _load_templates_with_prefetching(self, template_names: List[str], progress_callback: Optional[Callable[[str, float], None]] = None) -> List[TemplateEntry]:
        """Load templates with prefetching for better performance (with optional progress reporting)."""
        templates = []
        
        # Group template names by their storage file
        templates_by_file = {}
        for name in template_names:
            if name in self._index['templates']:
                storage_file = self._index['templates'][name]['storage_file']
                if storage_file not in templates_by_file:
                    templates_by_file[storage_file] = []
                templates_by_file[storage_file].append(name)
        
        # Load from each storage file with prefetching
        file_futures = {}
        
        # Start prefetching all files (lazy initialization)
        self._ensure_prefetch_executor()
        
        # Progress tracking across threads
        total_to_load = sum(len(v) for v in templates_by_file.values()) or 1
        progress_lock = threading.Lock()
        progress_state = {'loaded': 0, 'last_pct': -1}

        def _progress_hook(increment: int = 1):
            if increment <= 0:
                increment = 1
            with progress_lock:
                progress_state['loaded'] += increment
                # Throttle: only report every 50 templates and at completion
                should_emit = (progress_state['loaded'] % 50 == 0) or (progress_state['loaded'] >= total_to_load)
                if progress_callback is not None and should_emit:
                    pct = int((progress_state['loaded'] / total_to_load) * 100)
                    if pct != progress_state['last_pct']:
                        progress_state['last_pct'] = pct
                        try:
                            progress_callback(f"Loading templates {progress_state['loaded']}/{total_to_load}", float(pct))
                        except Exception:
                            pass
        for storage_file_path, file_template_names in templates_by_file.items():
            future = self._prefetch_executor.submit(
                self._load_templates_from_single_file, 
                storage_file_path, 
                file_template_names,
                _progress_hook
            )
            file_futures[storage_file_path] = future
        
        # Collect results as they complete
        for future in as_completed(file_futures.values()):
            try:
                file_templates = future.result()
                templates.extend(file_templates)
            except Exception as e:
                _LOG.error(f"Failed to load templates from storage file: {e}")
            
        # Ensure completion is reported
        try:
            if progress_callback is not None:
                progress_callback("Template loading complete", 100.0)
        except Exception:
            pass

        return templates
    
    def _load_templates_from_storage(self, template_names: List[str], progress_callback: Optional[Callable[[str, float], None]] = None) -> List[TemplateEntry]:
        """Load specific templates from type-specific HDF5 storage files (NO prefetching)."""
        templates = []
        
        # Group template names by their storage file
        templates_by_file = {}
        for name in template_names:
            if name in self._index['templates']:
                storage_file = self._index['templates'][name]['storage_file']
                if storage_file not in templates_by_file:
                    templates_by_file[storage_file] = []
                templates_by_file[storage_file].append(name)
        
        # Setup sequential progress tracker
        total_to_load = sum(len(v) for v in templates_by_file.values()) or 1
        loaded = 0

        def _progress_hook(increment: int = 1):
            nonlocal loaded
            if increment <= 0:
                increment = 1
            loaded += increment
            if progress_callback is not None:
                # Throttle: emit only every 50 templates or at completion
                should_emit = (loaded % 50 == 0) or (loaded >= total_to_load)
                if should_emit:
                    try:
                        pct = float(int((loaded / total_to_load) * 100))
                        progress_callback(f"Loading templates {loaded}/{total_to_load}", pct)
                    except Exception:
                        pass

        # Load from each storage file
        for storage_file_path, file_template_names in templates_by_file.items():
            file_templates = self._load_templates_from_single_file(storage_file_path, file_template_names, _progress_hook)
            templates.extend(file_templates)
        
        # Ensure completion is reported
        try:
            if progress_callback is not None:
                progress_callback("Template loading complete", 100.0)
        except Exception:
            pass

        return templates
    
    def _load_templates_from_single_file(self, storage_file_path: str, template_names: List[str], progress_hook: Optional[Callable[[int], None]] = None) -> List[TemplateEntry]:
        """Load templates from a single HDF5 file (optionally invoking a progress hook per template)."""
        templates = []
        
        try:
            # Resolve storage file path relative to template directory if it's not absolute
            if not Path(storage_file_path).is_absolute():
                storage_file_path = str(self.template_dir / storage_file_path)
            
            with h5py.File(storage_file_path, 'r') as f:
                # Check if this is a rebinned storage file
                metadata = f.get('metadata', {})
                is_rebinned = metadata.attrs.get('grid_rebinned', False)
                
                # Get the standard wavelength grid
                if 'standard_wavelength' in metadata:
                    wavelength_grid = metadata['standard_wavelength'][:]
                else:
                    # Fall back to our computed grid
                    wavelength_grid = self.standard_log_wave
                
                templates_group = f['templates']
                
                for name in template_names:
                    if name not in templates_group:
                        _LOG.warning(f"Template {name} not found in storage file {storage_file_path}")
                        continue
                
                    group = templates_group[name]
                    
                    # Load rebinned flux data
                    flux = group['flux'][:]
                    fft_real = group['fft_real'][:]
                    fft_imag = group['fft_imag'][:]
                    fft = fft_real + 1j * fft_imag
                    
                    # Load metadata
                    attrs = dict(group.attrs)
                    
                    # Load epoch data if present
                    epoch_data = []
                    if 'epochs' in group and attrs.get('epochs', 1) > 1:
                        epochs_group = group['epochs']
                        for epoch_name in epochs_group.keys():
                            epoch_group = epochs_group[epoch_name]
                            epoch_flux = epoch_group['flux'][:]
                            epoch_fft_real = epoch_group['fft_real'][:]
                            epoch_fft_imag = epoch_group['fft_imag'][:]
                            epoch_fft = epoch_fft_real + 1j * epoch_fft_imag
                            
                            epoch_info = {
                                'flux': epoch_flux,  # Already rebinned
                                'fft': epoch_fft,
                                'age': epoch_group.attrs.get('age', 0)
                            }
                            epoch_data.append(epoch_info)
                    
                    # Create template entry (flux is already rebinned)
                    template = TemplateEntry(
                        name=name,
                        type=attrs.get('type', 'Unknown'),
                        subtype=attrs.get('subtype', 'Unknown'),
                        age=attrs.get('age', 0),
                        redshift=attrs.get('redshift', 0),
                        phase=attrs.get('phase', 'Unknown'),
                        flux=flux,  # Already rebinned to standard grid
                        fft=fft,
                        epochs=attrs.get('epochs', 1),
                        epoch_data=epoch_data,
                        file_path=attrs.get('file_path', '')
                    )
                    
                    templates.append(template)

                    # progress per-template loaded
                    if progress_hook is not None:
                        try:
                            progress_hook(1)
                        except Exception:
                            pass
        
        except Exception as e:
            _LOG.error(f"Failed to load templates from storage file {storage_file_path}: {e}")
        
        return templates

    def get_template_info_for_gui(self) -> Dict[str, Any]:
        """
        Get template information in the format expected by GUI template discovery.
        
        This provides compatibility with the existing GUI template selection dialog
        that was designed for .lnw files.
        
        Returns
        -------
        Dict[str, Any]
            Template information in format compatible with snid.io.get_template_info()
        """
        if not self.is_built():
            return {
                'path': str(self.template_dir),
                'total': 0,
                'types': {},
                'templates': []
            }
        
        info = {
            'path': str(self.template_dir),
            'total': 0,
            'types': {},
            'templates': []
        }
        
        if not self._index:
            return info
        
        # Extract template information from index
        templates_dict = self._index.get('templates', {})
        
        for template_name, template_meta in templates_dict.items():
            template_type = template_meta.get('type', 'Unknown')
            subtype = template_meta.get('subtype', 'Unknown')
            age = template_meta.get('age', None)
            
            # Add to templates list
            info['templates'].append({
                'name': template_name,
                'type': template_type,
                'subtype': subtype,
                'age': age,
                'file': f"{template_name}.lnw"  # Virtual file name for compatibility
            })
            
            # Count by type
            if template_type not in info['types']:
                info['types'][template_type] = 0
            info['types'][template_type] += 1
        
        info['total'] = len(info['templates'])
        
        return info

    def get_all_template_names(self) -> List[str]:
        """
        Get a list of all available template names.
        
        Returns
        -------
        List[str]
            List of template names
        """
        if not self._index:
            return []
        
        return list(self._index.get('templates', {}).keys())
        
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists in the storage.
        
        Parameters
        ----------
        template_name : str
            Name of the template to check
            
        Returns
        -------
        bool
            True if template exists, False otherwise
        """
        if not self._index:
            return False
        
        return template_name in self._index.get('templates', {})


def create_unified_storage(template_dir: str, force_rebuild: bool = False, output_dir: str = None) -> TemplateFFTStorage:
    """
    Create or load unified template storage with rebinning.
    
    Parameters
    ----------
    template_dir : str
        Directory containing templates
    force_rebuild : bool, optional
        Force rebuild even if storage exists
    output_dir : str, optional
        Directory to write HDF5 and index files (default: template_dir)
    Returns
    -------
    TemplateFFTStorage
        Unified storage instance
    """
    storage = TemplateFFTStorage(template_dir, output_dir=output_dir)
    # Rebuild disabled; just return the storage instance
    return storage