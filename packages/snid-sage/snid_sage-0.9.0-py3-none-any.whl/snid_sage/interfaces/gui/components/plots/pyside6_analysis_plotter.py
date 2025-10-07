"""
SNID SAGE - PySide6 Analysis Plotter
====================================

Dedicated analysis plotter for PySide6 GUI that handles matplotlib-based analysis plots
including subtype proportions, redshift vs age plots, and threshold analysis.

This extracts the complex matplotlib plotting logic from the main GUI class to keep it clean.

Developed by Fiorenzo Stoppa for SNID SAGE
"""

import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict

# Matplotlib (Qt) unified import
try:
    from snid_sage.interfaces.gui.utils.matplotlib_qt import get_qt_mpl
    plt, Figure, FigureCanvas, _NavigationToolbar = get_qt_mpl()
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvas = None
    Figure = None

# PySide6 imports
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_analysis_plotter')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_analysis_plotter')


class PySide6AnalysisPlotter:
    """
    Handles matplotlib-based analysis plotting for PySide6 GUI
    
    This class manages:
    - Subtype proportions plots (pie chart, bar chart, threshold analysis)
    - Redshift vs age distribution plots
    - Data extraction from SNID results
    - Matplotlib figure and canvas management
    """
    
    def __init__(self, main_window, matplotlib_figure, matplotlib_canvas):
        """
        Initialize the analysis plotter
        
        Args:
            main_window: Reference to the main PySide6 GUI window
            matplotlib_figure: The matplotlib figure to plot on
            matplotlib_canvas: The matplotlib canvas for drawing
        """
        self.main_window = main_window
        self.matplotlib_figure = matplotlib_figure
        self.matplotlib_canvas = matplotlib_canvas
        self.app_controller = main_window.app_controller
        
        # Default subtype color mapping - use old GUI custom palette
        try:
            from snid_sage.snid.plotting import get_custom_color_palette
            custom_palette = get_custom_color_palette()
            self.custom_palette = custom_palette
        except ImportError:
            # Fallback colors if import fails
            self.custom_palette = [
                "#FF6361",  # coral
                "#BC5090",  # magenta
                "#58508D",  # purple
                "#003F5C",  # deep blue
                "#FFA600",  # amber
                "#B0B0B0",  # neutral grey
                "#912F40",  # cranberry
                "#5A6650",  # Muted Moss
                "#8C6D5C",  # Clay Taupe
                "#48788D",  # Dusty Blue
                "#9B5E4A",  # Muted Sienna
                "#6E4E6F",  # Smoky Plum
            ]
        
        # Keep basic subtype mapping for fallback
        self.subtype_colors = {
            'Unknown': '#A9A9A9',    # Gray
            '': '#CCCCCC',           # Light gray for empty
            None: '#999999'          # Gray for None
        }
    
    def create_subtype_proportions_plot(self):
        """Create subtype proportions plot in matplotlib with 3 panels like old GUI"""
        try:
            if not MATPLOTLIB_AVAILABLE:
                self._show_error("Matplotlib not available for analysis plots")
                return
            
            # Check if analysis results are available
            if not hasattr(self.app_controller, 'snid_results') or self.app_controller.snid_results is None:
                self._show_error("No analysis results available.\nPlease run the SNID analysis first.")
                return
            
            # Clear figure and create subplots like old GUI (2x2 grid with bottom spanning)
            self.matplotlib_figure.clear()
            gs = self.matplotlib_figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1])
            
            # Top left: Pie chart
            ax1 = self.matplotlib_figure.add_subplot(gs[0, 0])
            # Top right: Bar chart
            ax2 = self.matplotlib_figure.add_subplot(gs[0, 1])
            # Bottom: RLAP threshold analysis (spanning both columns)
            ax3 = self.matplotlib_figure.add_subplot(gs[1, :])
            
            # Extract cluster data
            cluster_data = self.extract_subtype_data()
            
            if not cluster_data:
                self._show_error("No cluster matches available for subtype analysis.")
                return
            
            cluster_matches = cluster_data['matches']
            cluster_type = cluster_data['type']
            
            # Calculate subtype proportions
            subtype_counts = defaultdict(int)
            subtype_rlaps = defaultdict(list)
            subtype_redshifts = defaultdict(list)
            
            for match in cluster_matches:
                template = match.get('template', {})
                subtype = template.get('subtype', 'Unknown')
                if not subtype or subtype.strip() == '':
                    subtype = 'Unknown'
                
                subtype_counts[subtype] += 1
                subtype_rlaps[subtype].append(match.get('rlap', 0))
                subtype_redshifts[subtype].append(match.get('redshift', 0))
            
            if not subtype_counts:
                self._show_error("No subtype data available.")
                return
            
            # Assign colors to all subtypes
            color_mapping = self._assign_subtype_colors(subtype_counts.keys())
            
            # Plot 1: Smaller pie chart
            sorted_subtypes = sorted(subtype_counts.items(), key=lambda x: x[1], reverse=True)
            labels = [item[0] for item in sorted_subtypes]
            values = [item[1] for item in sorted_subtypes]
            colors = [color_mapping.get(label, self.subtype_colors['Unknown']) for label in labels]
            
            # Create explode parameter - explode the winning subtype based on result.best_subtype (like CLI)
            winning_subtype = None
            result = self.app_controller.snid_results
            if hasattr(result, 'best_subtype') and result.best_subtype:
                winning_subtype = result.best_subtype
                
            explode = []
            for i, label in enumerate(labels):
                if winning_subtype and label == winning_subtype:
                    explode.append(0.1)  # Explode the winning subtype
                else:
                    explode.append(0)    # Keep other subtypes normal
            
            wedges, texts, autotexts = ax1.pie(
                values, labels=labels, autopct='%1.1f%%', colors=colors,
                explode=explode, startangle=90, textprops={'fontsize': 9}
            )
            
            # Style winning slice - match CLI by highlighting the winning subtype
            for i, (wedge, label) in enumerate(zip(wedges, labels)):
                if winning_subtype and label == winning_subtype:
                    wedge.set_edgecolor('black')
                    wedge.set_linewidth(2)
                else:
                    wedge.set_edgecolor('white')
                    wedge.set_linewidth(1)
            
            ax1.set_title(f'Subtype Distribution\n{cluster_type} Cluster', fontsize=11, fontweight='bold', pad=10)
            
            # Plot 2: Statistics table (like old GUI)
            self._create_statistics_table(ax2, subtype_counts, subtype_rlaps, subtype_redshifts, cluster_type)
            
            # Plot 3: RLAP threshold analysis (like old GUI)
            self.create_threshold_analysis(ax3, subtype_rlaps, color_mapping)
            
            # Tight layout and refresh
            self.matplotlib_figure.tight_layout()
            self.matplotlib_canvas.draw()
            
            _LOGGER.info(f"Created colorful subtype proportions plot with {len(subtype_counts)} subtypes and threshold analysis")
            
        except Exception as e:
            _LOGGER.error(f"Error creating subtype proportions plot: {e}")
            self._show_error(f"Error creating plot: {str(e)}")
    
    def create_redshift_age_plot(self):
        """Create redshift vs age plot from analysis results"""
        try:
            if not MATPLOTLIB_AVAILABLE:
                self._show_error("Matplotlib not available for analysis plots")
                return
            
            # Check if analysis results are available
            if not hasattr(self.app_controller, 'snid_results') or self.app_controller.snid_results is None:
                self._show_error("No analysis results available.\nPlease run the SNID analysis first.")
                return
            
            # Clear figure
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            
            # Extract plot data
            plot_data = self.extract_redshift_age_data()
            
            if not plot_data:
                self._show_error("No redshift-age data available for plotting.")
                return
            
            # Separate data by subtype instead of type
            subtype_data = defaultdict(list)
            for point in plot_data:
                subtype_data[point['subtype']].append(point)
            
            # Assign colors using custom palette from old GUI
            color_mapping = self._assign_subtype_colors(subtype_data.keys())
            
            for subtype, points in subtype_data.items():
                redshifts = [p['redshift'] for p in points]
                ages = [p['age'] for p in points]
                rlaps = [p['rlap'] for p in points]
                
                color = color_mapping.get(subtype, self.subtype_colors['Unknown'])
                
                # Use RLAP for point sizes
                sizes = [max(20, r * 3) for r in rlaps]
                
                scatter = ax.scatter(redshifts, ages, c=color, s=sizes, alpha=0.7, 
                                   label=f'{subtype} (n={len(points)})', edgecolors='black', linewidth=0.5)
            
            ax.set_xlabel('Redshift (z)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Age (days)', fontsize=12, fontweight='bold')
            ax.set_title('Redshift vs Age Distribution (by Subtype)', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10, loc='upper right')
            
            # Tight layout and refresh
            self.matplotlib_figure.tight_layout()
            self.matplotlib_canvas.draw()
            
            _LOGGER.info(f"Created redshift vs age plot with {len(plot_data)} data points colored by subtype")
            
        except Exception as e:
            _LOGGER.error(f"Error creating redshift vs age plot: {e}")
            self._show_error(f"Error creating plot: {str(e)}")
    
    def create_threshold_analysis(self, ax, subtype_rlaps, subtype_colors):
        """Create RLAP threshold analysis plot (bottom panel like old GUI)"""
        try:
            # Need cluster matches for proportion calculation like old GUI
            if not hasattr(self.app_controller, 'snid_results') or not self.app_controller.snid_results:
                ax.text(0.5, 0.5, "No analysis results available", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.axis('off')
                return
                
            result = self.app_controller.snid_results
            
            # Get cluster matches (same logic as data extraction)
            cluster_matches = []
            if (hasattr(result, 'clustering_results') and result.clustering_results and 
                'user_selected_cluster' in result.clustering_results and 
                result.clustering_results['user_selected_cluster']):
                user_cluster = result.clustering_results['user_selected_cluster']
                if 'matches' in user_cluster:
                    cluster_matches = user_cluster['matches']
            elif hasattr(result, 'filtered_matches') and result.filtered_matches:
                cluster_matches = result.filtered_matches
            elif hasattr(result, 'best_matches') and result.best_matches:
                cluster_matches = result.best_matches
            
            if not cluster_matches or not subtype_rlaps:
                ax.text(0.5, 0.5, "No RLAP data available", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.axis('off')
                return
            
            # Find RLAP range from all cluster matches
            all_rlaps = [match.get('rlap', 0) for match in cluster_matches if match.get('rlap', 0) > 0]
            
            if not all_rlaps:
                ax.text(0.5, 0.5, "No valid RLAP values", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.axis('off')
                return
            
            # Create RLAP thresholds (similar to old GUI)
            min_rlap = max(3.0, min(all_rlaps))  # Start from 3.0 or higher
            max_rlap = min(max(all_rlaps), 30.0)  # Cap at 30.0
            thresholds = np.linspace(min_rlap, max_rlap, 15)
            
            # Get sorted subtypes for consistent processing
            sorted_subtypes = sorted(subtype_rlaps.keys())
            
            # Calculate proportions at each threshold (like old GUI)
            subtype_proportions_by_threshold = {subtype: [] for subtype in sorted_subtypes}
            
            for threshold in thresholds:
                # Get all matches above this threshold
                qualified_matches = [match for match in cluster_matches 
                                   if match.get('rlap', 0) >= threshold]
                
                if qualified_matches:
                    # Count subtypes in qualified matches
                    threshold_subtype_counts = defaultdict(int)
                    for match in qualified_matches:
                        template = match.get('template', {})
                        subtype = template.get('subtype', 'Unknown')
                        if not subtype or subtype.strip() == '':
                            subtype = 'Unknown'
                        threshold_subtype_counts[subtype] += 1
                    
                    # Calculate proportions
                    total_qualified = len(qualified_matches)
                    for subtype in sorted_subtypes:
                        proportion = threshold_subtype_counts[subtype] / total_qualified if total_qualified > 0 else 0
                        subtype_proportions_by_threshold[subtype].append(proportion)
                else:
                    # No matches above threshold
                    for subtype in sorted_subtypes:
                        subtype_proportions_by_threshold[subtype].append(0)
            
            # Plot lines for each subtype that has non-zero proportions
            plotted_any = False
            for subtype, proportions in subtype_proportions_by_threshold.items():
                if any(p > 0 for p in proportions):  # Only plot if subtype has non-zero proportions
                    color = subtype_colors.get(subtype, self.subtype_colors['Unknown'])
                    ax.plot(thresholds, proportions, 'o-', label=subtype, 
                           color=color, linewidth=2, markersize=5)
                    plotted_any = True
            
            if plotted_any:
                ax.set_title('Subtype Proportions vs RLAP Threshold', fontsize=12, fontweight='bold', pad=15)
                ax.set_xlabel('RLAP Threshold', fontsize=10, fontweight='bold')
                ax.set_ylabel('Subtype Proportion', fontsize=10, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=9, loc='upper right')
                ax.set_ylim(-0.05, 1.05)  # Set y-axis limits like old GUI
                
                # Add vertical line at common threshold (5.0)
                if 5.0 >= min_rlap and 5.0 <= max_rlap:
                    ax.axvline(x=5.0, color='red', linestyle='--', alpha=0.7, linewidth=2)
                    ax.text(5.0, 0.9, 'RLAP=5', rotation=90, 
                           ha='right', va='top', color='red', fontsize=9, fontweight='bold')
            else:
                ax.text(0.5, 0.5, "Insufficient subtype diversity\nfor threshold analysis", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.axis('off')
            
        except Exception as e:
            _LOGGER.error(f"Error creating threshold analysis: {e}")
            ax.text(0.5, 0.5, f"Error creating threshold plot:\n{str(e)}", 
                   ha='center', va='center', transform=ax.transAxes, color='red')
    
    def extract_redshift_age_data(self):
        """Extract redshift vs age data from analysis results"""
        try:
            result = self.app_controller.snid_results
            
            # Extract matches with same priority as dialog implementation
            matches = []
            if (hasattr(result, 'clustering_results') and result.clustering_results and 
                'user_selected_cluster' in result.clustering_results and 
                result.clustering_results['user_selected_cluster']):
                user_cluster = result.clustering_results['user_selected_cluster']
                if 'matches' in user_cluster:
                    matches = user_cluster['matches']
            elif hasattr(result, 'filtered_matches') and result.filtered_matches:
                matches = result.filtered_matches
            elif hasattr(result, 'best_matches') and result.best_matches:
                matches = result.best_matches
            
            # Apply RLAP threshold filtering
            rlapmin = getattr(result, 'rlapmin', 5.0)
            filtered_matches = [m for m in matches if m.get('rlap', 0) >= rlapmin]
            
            # Extract plot data including subtype information
            plot_data = []
            for match in filtered_matches:
                z = match.get('redshift', None)
                age = match.get('age', None)
                sn_type = match.get('type', 'Unknown')
                rlap = match.get('rlap', 0)
                
                # Extract subtype from template
                template = match.get('template', {})
                subtype = template.get('subtype', 'Unknown') if isinstance(template, dict) else 'Unknown'
                if not subtype or subtype.strip() == '':
                    subtype = 'Unknown'
                
                if z is not None and age is not None:
                    plot_data.append({
                        'redshift': float(z),
                        'age': float(age),
                        'type': sn_type,
                        'subtype': subtype,
                        'rlap': float(rlap)
                    })
            
            return plot_data
            
        except Exception as e:
            _LOGGER.error(f"Error extracting redshift vs age data: {e}")
            return []
    
    def extract_subtype_data(self):
        """Extract subtype data from analysis results"""
        try:
            result = self.app_controller.snid_results
            
            # Extract cluster matches with same priority as dialog implementation
            cluster_matches = []
            cluster_type = "Unknown"
            
            if (hasattr(result, 'clustering_results') and result.clustering_results and 
                'user_selected_cluster' in result.clustering_results and 
                result.clustering_results['user_selected_cluster']):
                selected_cluster = result.clustering_results['user_selected_cluster']
                if 'matches' in selected_cluster:
                    cluster_matches = selected_cluster['matches']
                    cluster_type = selected_cluster.get('type', 'Unknown')
            elif hasattr(result, 'filtered_matches') and result.filtered_matches:
                cluster_matches = result.filtered_matches
                if cluster_matches:
                    cluster_type = cluster_matches[0].get('type', 'Unknown')
            elif hasattr(result, 'best_matches') and result.best_matches:
                cluster_matches = result.best_matches
                if cluster_matches:
                    cluster_type = cluster_matches[0].get('type', 'Unknown')
            
            return {
                'matches': cluster_matches,
                'type': cluster_type
            }
            
        except Exception as e:
            _LOGGER.error(f"Error extracting subtype data: {e}")
            return None
    
    def _assign_subtype_colors(self, subtypes):
        """Assign colors to all subtypes, using custom palette from old GUI"""
        color_mapping = {}
        color_idx = 0
        
        # Sort subtypes for consistent assignment
        sorted_subtypes = sorted(subtypes)
        
        for subtype in sorted_subtypes:
            if subtype in self.subtype_colors:
                color_mapping[subtype] = self.subtype_colors[subtype]
            else:
                color_mapping[subtype] = self.custom_palette[color_idx % len(self.custom_palette)]
                color_idx += 1
        
        return color_mapping
    
    def _create_statistics_table(self, ax, subtype_counts, subtype_rlaps, subtype_redshifts, cluster_type):
        """Create a text-based statistics table on the right side of the plot."""
        ax.axis('off')  # Hide the axis
        
        # Calculate statistics
        total_matches = sum(subtype_counts.values())
        if total_matches == 0:
            ax.text(0.5, 0.5, "No data to display.", ha='center', va='center', 
                   transform=ax.transAxes, fontsize=10)
            return
        
        # Create table data similar to old GUI
        table_data = []
        headers = ['Subtype', 'Count', '%', 'Avg RLAP', 'Avg Z']
        
        # Sort subtypes by count (descending)
        sorted_subtypes = sorted(subtype_counts.items(), key=lambda x: x[1], reverse=True)
        
        for subtype, count in sorted_subtypes:
            percentage = (count / total_matches) * 100
            avg_rlap = np.mean(subtype_rlaps[subtype]) if subtype_rlaps[subtype] else 0
            avg_z = np.mean(subtype_redshifts[subtype]) if subtype_redshifts[subtype] else 0
            
            table_data.append([
                subtype,
                str(count),
                f"{percentage:.1f}%",
                f"{avg_rlap:.1f}",
                f"{avg_z:.4f}"
            ])
        
        # Create formatted table text
        col_widths = [12, 6, 8, 10, 10]  # Column widths
        
        # Format header
        header_text = ""
        for i, header in enumerate(headers):
            header_text += f"{header:<{col_widths[i]}}"
        header_text += "\n" + "-" * sum(col_widths) + "\n"
        
        # Format data rows
        table_text = header_text
        for row in table_data:
            row_text = ""
            for i, cell in enumerate(row):
                row_text += f"{cell:<{col_widths[i]}}"
            table_text += row_text + "\n"
        
        # Display the table
        ax.text(0.02, 0.98, "Subtype Statistics", ha='left', va='top', 
               transform=ax.transAxes, fontsize=11, fontweight='bold')
        ax.text(0.02, 0.85, table_text, ha='left', va='top', 
               transform=ax.transAxes, fontsize=8, fontfamily='monospace')
    
    def _show_error(self, error_msg):
        """Show error message in matplotlib plot area"""
        try:
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            ax.text(0.5, 0.5, error_msg, ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_title('Plot Error', fontsize=14, fontweight='bold', color='red')
            ax.axis('off')
            self.matplotlib_canvas.draw()
        except Exception as e:
            _LOGGER.error(f"Error showing matplotlib error: {e}") 