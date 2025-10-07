"""
snidtype.py – post-processing / typing / statistics for the Python SNID port
============================================================================

This module implements the exact type determination logic from Fortran SNID,
including template ranking, type fractions, slopes, and security assessment.

Public API
----------
SNIDResult                       *dataclass container* returned by run_snid
determine_best_type_fortran      *main function* - complete Fortran pipeline
compute_type_fractions           weighted fractions of each SN type
compute_subtype_fractions        same for sub-types
compute_consensus_z_age          ensemble ⟨z⟩, ⟨age⟩ with covariance
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Set, Optional
from collections import Counter, defaultdict
import logging

# ----------------------------------------------------------------------
# 0.  Constants from Fortran SNID.INC
# ----------------------------------------------------------------------
RLAP_MIN   = 5.0
LAP_MIN    = 0.4
# Z_FILTER constant removed (deprecated)
EPSFRAC    = 0.01
EPSSLOPE   = 0.01
EPSRLAP    = 0.01  # For multiple best template check
MAXRLAP    = 100   # Maximum rlap value for slope calculations

# DEPRECATED: Legacy RLAP security thresholds removed
# Use cluster-based security assessment from cosmological_clustering.py instead

# Fortran type mapping (from enhanced typeinfo.f - 13 types, 70+ subtypes)
TYPENAME = {
    # Type 1 - SN Ia (10 subtypes)
    1: {1: 'Ia', 2: 'Ia-norm', 3: 'Ia-91T', 4: 'Ia-91bg', 5: 'Ia-csm', 6: 'Ia-pec', 
        7: 'Ia-02cx', 8: 'Ia-03fg', 9: 'Ia-02es', 10: 'Ia-Ca-rich'},
    
    # Type 2 - SN Ib (7 subtypes)
    2: {1: 'Ib', 2: 'Ib-norm', 3: 'Ib-pec', 4: 'IIb', 5: 'Ibn', 6: 'Ib-Ca-rich', 7: 'Ib-csm'},
    
    # Type 3 - SN Ic (7 subtypes)
    3: {1: 'Ic', 2: 'Ic-norm', 3: 'Ic-pec', 4: 'Ic-broad', 5: 'Icn', 6: 'Ic-Ca-rich', 7: 'Ic-csm'},
    
    # Type 4 - SN II (6 subtypes)
    4: {1: 'II', 2: 'IIP', 3: 'II-pec', 4: 'IIn', 5: 'IIL', 6: 'IIn-pec'},
    
    # Type 5 - NotSN (9 subtypes) - LEGACY, kept for backward compatibility
    5: {1: 'NotSN', 2: 'AGN', 3: 'Gal', 4: 'QSO', 5: 'M-star', 6: 'C-star', 
        7: 'Afterglow', 8: 'Nova', 9: 'CV'},
    
    # Type 6 - SLSN (6 subtypes)
    6: {1: 'SLSN', 2: 'SLSN-I', 3: 'SLSN-Ib', 4: 'SLSN-Ic', 5: 'SLSN-II', 6: 'SLSN-IIn'},
    
    # Type 7 - LFBOT (3 subtypes)
    7: {1: 'LFBOT', 2: '18cow', 3: '20xnd'},
    
    # Type 8 - TDE (5 subtypes)
    8: {1: 'TDE', 2: 'TDE-H', 3: 'TDE-He', 4: 'TDE-H-He', 5: 'TDE-Ftless'},
    
    # Type 9 - KN (2 subtypes)
    9: {1: 'KN', 2: '17gfo'},
    
    # Type 10 - GAP (4 subtypes)
    10: {1: 'GAP', 2: 'LRN', 3: 'LBV', 4: 'ILRT'},
    
    # Type 11 - Galaxy (7 subtypes)
    11: {1: 'Galaxy', 2: 'Gal-E', 3: 'Gal-S0', 4: 'Gal-Sa', 5: 'Gal-Sb', 
         6: 'Gal-Sc', 7: 'Gal-SB'},
    
    # Type 12 - Star (3 subtypes)
    12: {1: 'Star', 2: 'M-star', 3: 'C-star'},
    
    # Type 13 - AGN (3 subtypes)
    13: {1: 'AGN', 2: 'AGN-type1', 3: 'QSO'}
}

# Reverse mapping (string to type indices)
TYPE_TO_INDICES = {}
for it, subtypes in TYPENAME.items():
    for ist, name in subtypes.items():
        TYPE_TO_INDICES[name] = (it, ist)

# Flat type to hierarchical main type mapping (for templates using flat structure)
FLAT_TO_MAIN_TYPE = {
    # Core types that are already main types
    'Ia': 'Ia', 'Ib': 'Ib', 'Ic': 'Ic', 'II': 'II', 'NotSN': 'NotSN',
    
    # SLSN subtypes → SLSN main type
    'SLSN': 'SLSN', 'SLSN-I': 'SLSN', 'SLSN-Ib': 'SLSN', 'SLSN-Ic': 'SLSN', 
    'SLSN-II': 'SLSN', 'SLSN-IIn': 'SLSN',
    
    # LFBOT subtypes → LFBOT main type
    'LFBOT': 'LFBOT', '18cow': 'LFBOT', '20xnd': 'LFBOT',
    
    # TDE subtypes → TDE main type
    'TDE': 'TDE', 'TDE-H': 'TDE', 'TDE-He': 'TDE', 'TDE-H-He': 'TDE', 'TDE-Ftless': 'TDE',
    
    # KN subtypes → KN main type
    'KN': 'KN', '17gfo': 'KN',
    
    # GAP subtypes → GAP main type (but often used as main types in templates)
    'GAP': 'GAP', 'LRN': 'GAP', 'LBV': 'GAP', 'ILRT': 'GAP',
    
    # NEW: Galaxy subtypes → Galaxy main type
    'Galaxy': 'Galaxy', 'Gal': 'Galaxy', 'Gal-E': 'Galaxy', 'Gal-S0': 'Galaxy',
    'Gal-Sa': 'Galaxy', 'Gal-Sb': 'Galaxy', 'Gal-Sc': 'Galaxy', 'Gal-SB': 'Galaxy',
    
    # NEW: Star subtypes → Star main type
    'Star': 'Star', 'M-star': 'Star', 'C-star': 'Star',
    
    # NEW: AGN subtypes → AGN main type
    'AGN': 'AGN', 'AGN-type1': 'AGN', 'QSO': 'AGN',
    
    # NotSN subtypes (LEGACY - for backward compatibility)
    'Afterglow': 'GAP', 'Nova': 'GAP', 'CV': 'Star',
    
    # Special cases found in your templates
    'US-Ic': 'Ic'  # Ultra-stripped Type Ic
}

def get_main_type_from_template(template_type: str) -> str:
    """
    Convert template type (which may be flat) to hierarchical main type.
    
    Parameters
    ----------
    template_type : str
        Type from template (e.g., 'SLSN-I', 'TDE-He', 'Ia-norm')
        
    Returns
    -------
    str
        Main type for classification (e.g., 'SLSN', 'TDE', 'Ia')
    """
    # Handle hierarchical subtypes (e.g., 'Ia-norm' → 'Ia')
    if template_type.startswith(('Ia-', 'Ib-', 'Ic-', 'II')):
        if template_type.startswith('Ia-'):
            return 'Ia'
        elif template_type.startswith('Ib-'):
            return 'Ib'
        elif template_type.startswith('Ic-'):
            return 'Ic'
        elif template_type.startswith('II'):
            return 'II'
    
    # Use flat-to-main mapping
    return FLAT_TO_MAIN_TYPE.get(template_type, template_type)

def get_type_indices_from_template(template_type: str, template_subtype: str = "") -> Tuple[int, int]:
    """
    Get type indices for a template, handling both hierarchical and flat structures.
    
    Parameters
    ----------
    template_type : str
        Main type from template
    template_subtype : str, optional
        Subtype from template (if available)
        
    Returns
    -------
    Tuple[int, int]
        (main_type_index, subtype_index) for TYPENAME lookup
    """
    # Use subtype if available, otherwise use type
    lookup_name = template_subtype if template_subtype else template_type
    
    # Try direct lookup first
    if lookup_name in TYPE_TO_INDICES:
        return TYPE_TO_INDICES[lookup_name]
    
    # Try to find by main type classification
    main_type = get_main_type_from_template(template_type)
    
    # Look for main type in TYPENAME
    for it, subtypes in TYPENAME.items():
        if subtypes.get(1) == main_type:  # Check if this is the main type
            # Default to main type (ist=1) if subtype not found
            return (it, 1)
    
    # Fallback to unknown
    return (0, 0)

# ----------------------------------------------------------------------
# 1.  Result container
# ----------------------------------------------------------------------
@dataclass
class SNIDResult:
    """
    Container for SNID results with all match information and statistics.
    """
    # Status / bookkeeping
    success: bool = False
    runtime_sec: float = 0.0
    
    # Input spectrum data
    input_spectrum: Dict[str, np.ndarray] = field(default_factory=dict)
    processed_spectrum: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Template matches
    best_matches: List[Dict[str, Any]] = field(default_factory=list)
    filtered_matches: List[Dict[str, Any]] = field(default_factory=list)  # GMM-filtered matches
    top_matches: List[Dict[str, Any]] = field(default_factory=list)  # Top N matches for output files
    
    # Basic match parameters
    r: float = 0.0
    lap: float = 0.0
    rlap: float = 0.0
    redshift: float = 0.0
    redshift_error: float = 0.0
    template_name: str = "Unknown"
    template_type: str = "Unknown"
    template_subtype: str = ""
    template_age: float = 0.0
    
    # Consensus values
    initial_redshift: float = 0.0
    consensus_redshift: float = 0.0
    consensus_redshift_error: float = 0.0
    consensus_z_median: float = 0.0
    consensus_age: float = 0.0
    consensus_age_error: float = 0.0
    consensus_type: str = "Unknown"
    best_subtype: str = "Unknown"
    type_confidence: float = 0.0
    subtype_confidence: float = 0.0  # NEW: Probabilistic subtype confidence from cluster-aware method

    
    # Statistics
    match_statistics: Dict[str, Any] = field(default_factory=dict)
    type_fractions: Dict[str, float] = field(default_factory=dict)
    type_fractions_weighted: Dict[str, float] = field(default_factory=dict)
    type_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Additional comprehensive statistics (matching Fortran SNID)
    type_slopes: Dict[str, float] = field(default_factory=dict)
    subtype_fractions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    template_rankings: Dict[str, List[int]] = field(default_factory=dict)
    correlation_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Grid parameters
    dwlog: float | None = None
    min_rlap: float | None = None
    log_wave: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Output files
    output_files: Dict[str, str] = field(default_factory=dict)
    input_file: str = ""

    def __str__(self) -> str:
        if not self.success:
            return "SNID run failed."
        
        # ENHANCED: More informative and prominent result display
        lines = []
        
        # Primary classification line with enhanced formatting
        redshift_str = f"z = {self.redshift:.5f}"
        if hasattr(self, 'redshift_error') and self.redshift_error > 0:
            redshift_str += f" ± {self.redshift_error:.5f}"
        
        quality_str = f"RLAP = {self.rlap:.2f}"
        
        # Enhanced type/subtype display with confidence
        if self.consensus_type and self.consensus_type != "Unknown":
            type_str = self.consensus_type
            
            # Add subtype with confidence if available
            if (self.best_subtype and self.best_subtype != "Unknown" and 
                hasattr(self, 'subtype_confidence') and self.subtype_confidence > 0):
                
                # Convert confidence to descriptive level (qualitative only like CLI)
                if self.subtype_confidence > 0.7:
                    conf_icon = "🔒"
                    conf_desc = "High"
                elif self.subtype_confidence > 0.4:
                    conf_icon = "🔓"
                    conf_desc = "Medium"
                else:
                    conf_icon = "🔑"
                    conf_desc = "Low"
                
                type_str += f" / {self.best_subtype} ({conf_icon} {conf_desc})"
            elif self.best_subtype and self.best_subtype != "Unknown":
                type_str += f" / {self.best_subtype}"
            

        else:
            type_str = "Unknown (❌ FAILED)"
        
        # Clustering information if available
        cluster_info = ""
        if (hasattr(self, 'clustering_results') and self.clustering_results and 
            self.clustering_results.get('success')):
            cluster = self.clustering_results.get('best_cluster')
            if cluster:
                cluster_size = cluster.get('size', 0)
                cluster_score = cluster.get('composite_score', 0)
                top_5_mean = cluster.get('top_5_mean', 0)
                cluster_info = f"   🎯 Cluster: {cluster_size} templates (top-5 mean: {top_5_mean:.2f}, score: {cluster_score:.2f})"
        
        # Consensus redshift if different from template redshift
        consensus_info = ""
        if (hasattr(self, 'consensus_redshift') and self.consensus_redshift > 0 and 
            abs(self.consensus_redshift - self.redshift) > 0.001):
            consensus_info = f"   📊 Consensus z = {self.consensus_redshift:.5f}"
            if hasattr(self, 'consensus_redshift_error') and self.consensus_redshift_error > 0:
                consensus_info += f" ± {self.consensus_redshift_error:.5f}"
        
        # Build the final string with clearer hierarchy
        lines.append("=" * 60)
        lines.append(f"🏷️  Classification: {type_str}")
        lines.append(f"🔴 {redshift_str}   ⭐ {quality_str}")
        lines.append("=" * 60)
        
        if cluster_info:
            lines.append(cluster_info)
        if consensus_info:
            lines.append(consensus_info)
        
        return "\n".join(lines)


# ----------------------------------------------------------------------
# 2.  Helper functions
# ----------------------------------------------------------------------
def weighted_mean(vals: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    """
    LEGACY FUNCTION - DEPRECATED
    
    This function is deprecated and should not be used for new code.
    Use calculate_weighted_redshift or calculate_weighted_age instead.
    
    Maintained only for backwards compatibility with legacy template type analysis.
    """
    logger = logging.getLogger(__name__)
    logger.warning("Using deprecated weighted_mean function. Use proper statistical methods instead.")
    
    # Simple fallback for legacy compatibility only
    if len(vals) == 0:
        return 0.0, 0.0
    
    if len(vals) == 1:
        return float(vals[0]), 0.0
    
    # Basic weighted calculation for backwards compatibility only
    try:
        from snid_sage.shared.utils.math_utils import calculate_weighted_redshift
        # Use uniform weights since this is legacy compatibility
        weights = np.ones_like(vals)
        result_mean, result_uncertainty = calculate_weighted_redshift(vals, weights)
        return result_mean, result_uncertainty
    except ImportError:
        # Ultimate fallback
        return float(np.mean(vals)), float(np.std(vals) / np.sqrt(len(vals)))


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    """Calculate weighted median of a dataset."""
    if len(values) == 0:
        return 0.0
    if len(values) == 1:
        return float(values[0])
        
    # Sort values and weights together
    idx = np.argsort(values)
    sorted_values = values[idx]
    sorted_weights = weights[idx]
    
    # Calculate cumulative weight
    cumw = np.cumsum(sorted_weights)
    
    # Find median at half of total weight
    half = cumw[-1] / 2.0
    idx = np.searchsorted(cumw, half)
    
    if idx >= len(values):  # Safety check
        return float(sorted_values[-1])
    
    return float(sorted_values[idx])


def linear_fit_weighted(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    """Weighted linear regression returning slope and intercept."""
    if len(x) < 2:
        return 0.0, 0.0
        
    # Weighted fit
    sw = w.sum()
    if sw == 0:
        return 0.0, 0.0
        
    wx = w * x
    wy = w * y
    swx = wx.sum()
    swy = wy.sum()
    swxx = (wx * x).sum()
    swxy = (wx * y).sum()
    
    delta = sw * swxx - swx * swx
    if delta == 0:
        return 0.0, 0.0
        
    a0 = (swxx * swy - swx * swxy) / delta  # intercept
    a1 = (sw * swxy - swx * swy) / delta    # slope
    
    return a1, a0


# ----------------------------------------------------------------------
# 3.  Core statistics functions (following Fortran logic exactly)
# ----------------------------------------------------------------------
def compute_type_subtype_stats(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute redshift/age statistics by type and subtype.
    Following Fortran getzt logic.
    """
    if not matches:
        return {}
    
    # Group by type and subtype
    type_groups = {}
    for m in matches:
        tp = m['template'].get('type', 'Unknown')
        sub = m['template'].get('subtype', 'Unknown')
        
        if tp not in type_groups:
            type_groups[tp] = {'_all': [], 'subtypes': {}}
        
        type_groups[tp]['_all'].append(m)
        
        if sub not in type_groups[tp]['subtypes']:
            type_groups[tp]['subtypes'][sub] = []
        type_groups[tp]['subtypes'][sub].append(m)
    
    # Compute statistics for each group
    stats = {}
    for tp, data in type_groups.items():
        stats[tp] = {}
        
        # Type-level statistics
        all_matches = data['_all']
        z_vals = np.array([m['redshift'] for m in all_matches])
        # Use RLAP-cos if available, otherwise RLAP
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        rlap_weights = np.array([get_best_metric_value(m) for m in all_matches])
        
        z_median = weighted_median(z_vals, rlap_weights)
        z_mean, z_std = weighted_mean(z_vals, rlap_weights)
        
        # Age statistics
        age_vals = []
        age_weights = []
        for m in all_matches:
            age = m.get('age', m['template'].get('age', 0.0))
            age_flag = m['template'].get('age_flag', 0)
            if age_flag == 0:
                age_vals.append(age)
                # Use RLAP-cos if available, otherwise RLAP
                age_weights.append(get_best_metric_value(m))
        
        if age_vals:
            age_vals = np.array(age_vals)
            age_weights = np.array(age_weights)
            age_median = weighted_median(age_vals, age_weights)
            age_mean, age_std = weighted_mean(age_vals, age_weights)
        else:
            age_median = age_mean = age_std = 0.0
        
        stats[tp]['_all'] = {
            'z_median': z_median, 'z_mean': z_mean, 'z_std': z_std,
            'age_median': age_median, 'age_mean': age_mean, 'age_std': age_std,
            'count': len(all_matches)
        }
        
        # Subtype-level statistics
        for sub, sub_matches in data['subtypes'].items():
            if len(sub_matches) == 0:
                continue
                
            z_vals = np.array([m['redshift'] for m in sub_matches])
            # Use RLAP-cos if available, otherwise RLAP
            rlap_weights = np.array([get_best_metric_value(m) for m in sub_matches])
            
            z_median = weighted_median(z_vals, rlap_weights)
            z_mean, z_std = weighted_mean(z_vals, rlap_weights)
            
            # Age statistics
            age_vals = []
            age_weights = []
            for m in sub_matches:
                age = m.get('age', m['template'].get('age', 0.0))
                age_flag = m['template'].get('age_flag', 0)
                if age_flag == 0:
                    age_vals.append(age)
                    # Use RLAP-cos if available, otherwise RLAP
                    age_weights.append(get_best_metric_value(m))
            
            if age_vals:
                age_vals = np.array(age_vals)
                age_weights = np.array(age_weights)
                age_median = weighted_median(age_vals, age_weights)
                age_mean, age_std = weighted_mean(age_vals, age_weights)
            else:
                age_median = age_mean = age_std = 0.0
            
            stats[tp][sub] = {
                'z_median': z_median, 'z_mean': z_mean, 'z_std': z_std,
                'age_median': age_median, 'age_mean': age_mean, 'age_std': age_std,
                'count': len(sub_matches)
            }
    
    return stats

# ----------------------------------------------------------------------
# 5.  Simplified API functions (for backward compatibility)
# ----------------------------------------------------------------------
def compute_type_fractions(matches: List[Dict[str, Any]], 
                          weighted: bool = False) -> Dict[str, float]:
    """Compute type fractions from matches."""
    if not matches:
        return {}
        
    type_values = defaultdict(float)
    
    for m in matches:
        tp = m['template'].get('type', 'Unknown')
        value = m['rlap'] if weighted else 1.0
        type_values[tp] += value
    
    total = sum(type_values.values())
    if total > 0:
        return {tp: val/total for tp, val in type_values.items()}
    else:
        return {}


def compute_subtype_fractions(matches: List[Dict[str, Any]], 
                             weighted: bool = True) -> Dict[str, Dict[str, float]]:
    """Compute subtype fractions from matches."""
    if not matches:
        return {}
        
    type_subtype_values = defaultdict(lambda: defaultdict(float))
    
    for m in matches:
        tp = m['template'].get('type', 'Unknown')
        sub = m['template'].get('subtype', 'Unknown')
        value = m['rlap'] if weighted else 1.0
        type_subtype_values[tp][sub] += value
    
    result = {}
    for tp, subtypes in type_subtype_values.items():
        total = sum(subtypes.values())
        if total > 0:
            result[tp] = {sub: val/total for sub, val in subtypes.items()}
        else:
            result[tp] = {sub: 0.0 for sub in subtypes}
    
    return result


def compute_initial_redshift(matches: List[Dict[str, Any]]) -> float:
    """Compute initial redshift estimate using weighted median approach."""
    if not matches:
        return 0.0
        
    # Create weighted redshift list based on rlap values
    redshifts = []
    weights = []
    
    for match in matches:
        rlap = match['rlap']
        z = match['redshift']
        
        # Add multiple copies based on rlap thresholds (like Fortran)
        if rlap > 4:
            redshifts.append(z)
            weights.append(1)
        if rlap > 5:
            redshifts.extend([z, z])
            weights.extend([1, 1])
        if rlap > 6:
            redshifts.extend([z, z])
            weights.extend([1, 1])
    
    if not redshifts:
        return 0.0
        
    return weighted_median(np.array(redshifts), np.array(weights))


# ----------------------------------------------------------------------
# 6.  Legacy functions (for backward compatibility)
# ----------------------------------------------------------------------
def determine_best_type(matches: List[Dict[str, Any]], 
                       min_rlap: float = RLAP_MIN) -> str:
    """Legacy function - use determine_best_type_fortran instead."""
    if not matches:
        return 'Unknown'
    
    # Simple type determination based on highest rlap
    good_matches = [m for m in matches if m['rlap'] >= min_rlap]
    if not good_matches:
        return 'Unknown'
    
    # Return type of best match
    return good_matches[0]['template'].get('type', 'Unknown')


def determine_type_security_detailed(matches: List[Dict[str, Any]], 
                                   consensus_type: str,
                                   min_rlap: float = RLAP_MIN) -> Dict[str, Any]:
    """Legacy function - use determine_best_type_fortran instead."""
    good_matches = [m for m in matches if m['rlap'] >= min_rlap]
    if not good_matches:
        return {'secure': False, 'score': 0, 'details': {}}
    
    # Simple security check
    type_matches = [m for m in good_matches if m['template'].get('type') == consensus_type]
    score = len(type_matches) / len(good_matches) * 5  # Scale to 0-5
    
    return {
        'secure': score >= 3,
        'score': int(score),
        'details': {'type_fraction': len(type_matches) / len(good_matches)}
    }


# ----------------------------------------------------------------------
# 7.  Exports
# ----------------------------------------------------------------------
__all__ = [
    "SNIDResult",
    "compute_type_fractions", "compute_subtype_fractions",
    "compute_initial_redshift",
    # Legacy functions (simplified)
    "determine_best_type", "determine_type_security_detailed",
    # Utility functions
    "get_main_type_from_template", "get_type_indices_from_template",
    "weighted_mean", "weighted_median", "linear_fit_weighted",
    # Constants
    "RLAP_MIN", "MAXRLAP", "EPSRLAP", "EPSFRAC"
]