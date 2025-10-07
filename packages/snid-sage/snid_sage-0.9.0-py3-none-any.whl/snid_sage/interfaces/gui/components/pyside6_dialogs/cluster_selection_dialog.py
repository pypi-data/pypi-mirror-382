"""
SNID SAGE - Cluster Selection Dialog - PySide6 Version with Matplotlib
=====================================================

Interactive GMM cluster selection dialog for SNID analysis results.
Allows users to select the best cluster from GMM clustering results.

Features:
- Interactive matplotlib 3D plots of cluster visualization
- Cluster dropdown selector for easy selection  
- Top 2 template matches panel with spectrum overlays
- Real-time cluster selection feedback
- Automatic fallback to best cluster
- Modern Qt styling matching other dialogs
"""

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable

# Matplotlib for 3D plotting (Qt helper)
try:
    from snid_sage.interfaces.gui.utils.matplotlib_qt import get_qt_mpl
    plt, Figure, FigureCanvas, _NavigationToolbar = get_qt_mpl()
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvas = None
    Figure = None

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_cluster_selection')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_cluster_selection')

# Import math utilities
try:
    from snid_sage.shared.utils.math_utils import get_best_metric_value, get_metric_name_for_match
    MATH_UTILS_AVAILABLE = True
except ImportError:
    MATH_UTILS_AVAILABLE = False

# Import string utility to clean template names (with safe fallback)
try:
    from snid_sage.shared.utils import clean_template_name  # type: ignore
except Exception:
    def clean_template_name(name):
        return name


class PySide6ClusterSelectionDialog(QtWidgets.QDialog):
    """
    Interactive GMM cluster selection dialog for SNID analysis results.
    
    This dialog provides:
    - Interactive 3D cluster visualization using matplotlib
    - Cluster dropdown selection 
    - Top 2 template matches with spectrum overlays
    - Real-time cluster selection feedback
    - Automatic best cluster fallback
    """
    
    def __init__(self, parent=None, clusters=None, snid_result=None, callback=None):
        """
        Initialize cluster selection dialog
        
        Args:
            parent: Parent widget
            clusters: List of cluster candidates 
            snid_result: SNID analysis results
            callback: Callback function when cluster is selected
        """
        super().__init__(parent)
        # Ensure this dialog fully deletes its widgets when closed to avoid stale references
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        # Store input data
        self.all_candidates = clusters or []
        self.snid_result = snid_result
        self.callback = callback
        
        # Selection state
        self.selected_cluster = None
        self.selected_index = -1
        
        # Get automatic best from clustering results
        self.automatic_best = None
        if hasattr(snid_result, 'clustering_results') and snid_result.clustering_results:
            self.automatic_best = snid_result.clustering_results.get('best_cluster')
        if not self.automatic_best and self.all_candidates:
            self.automatic_best = self.all_candidates[0]
        
        # Sort candidates by score
        self._sort_candidates()
        
        # UI components
        self.cluster_dropdown = None
        self.plot_widget = None  # Matplotlib canvas
        self.matches_canvas = None  # Matplotlib canvas for matches
        self.scatter_plots = []  # Store scatter plot objects for highlighting
        self.fig = None  # Main 3D plot figure
        self.ax = None   # Main 3D plot axes
        self.matches_fig = None  # Matches figure
        self.matches_axes = []   # Matches subplot axes
        self.scatter_to_index = {}  # Map matplotlib scatter artists to cluster indices
        
        # Colors for different supernova types
        self.type_colors = self._get_type_colors()
        
        # Validate matplotlib availability
        if not MATPLOTLIB_AVAILABLE:
            QtWidgets.QMessageBox.warning(
                self, "Missing Dependency", 
                "Matplotlib is required for cluster visualization.\n"
                "Please ensure matplotlib is installed."
            )
        
        # Validate input data
        if not self.all_candidates:
            QtWidgets.QMessageBox.warning(
                self, "No Clusters", 
                "No cluster candidates available.\n"
                "This dialog will automatically use the best available result."
            )
            # Auto-close and use automatic fallback
            QtCore.QTimer.singleShot(100, self._auto_select_and_close)
            return
        
        try:
            self._setup_ui()
            self._populate_data()
            
            # Auto-select the automatic best cluster
            if self.all_candidates:
                best_index = self._find_automatic_best_index()
                self._select_cluster(best_index)
                
        except Exception as e:
            _LOGGER.error(f"Error initializing cluster selection dialog: {e}")
            QtWidgets.QMessageBox.critical(
                self, "Initialization Error",
                f"Failed to initialize cluster selection dialog:\n{e}\n\n"
                "Will use automatic cluster selection."
            )
            QtCore.QTimer.singleShot(100, self._auto_select_and_close)
    
    def _sort_candidates(self):
        """Sort candidates by score"""
        def _get_candidate_score(c):
            # Preferred metric hierarchy: penalised_score → composite_score → mean_metric (RLAP-CCC/RLAP)
            return (
                c.get('penalized_score') or
                c.get('penalised_score') or  # British spelling safeguard
                c.get('composite_score') or
                c.get('mean_rlap') or 0.0
            )

        try:
            self.all_candidates.sort(key=_get_candidate_score, reverse=True)
        except Exception as sort_err:
            _LOGGER.debug(f"Could not sort clusters by score: {sort_err}")
    
    def _find_automatic_best_index(self):
        """Find index of automatic best cluster after sorting"""
        if not self.automatic_best:
            return 0
        
        # Try direct object identity first
        try:
            return self.all_candidates.index(self.automatic_best)
        except ValueError:
            pass
        
        # Fallback by (type, cluster_id)
        t_type = self.automatic_best.get('type')
        t_id = self.automatic_best.get('cluster_id')
        for idx, cand in enumerate(self.all_candidates):
            if cand.get('type') == t_type and cand.get('cluster_id') == t_id:
                return idx
        return 0
    
    def _get_type_colors(self):
        """Get color mapping for supernova types"""
        return {
            'Ia': '#FFB3B3',      # Pastel Red
            'Ib': '#FFCC99',      # Pastel Orange  
            'Ic': '#99CCFF',      # Pastel Blue
            'II': '#9370DB',      # Medium slate blue
            'Galaxy': '#8A2BE2',  # Blue-violet for galaxies
            'Star': '#FFD700',    # Gold for stars
            'AGN': '#FF6347',     # Tomato red for AGN/QSO
            'SLSN': '#20B2AA',    # Light sea green
            'LFBOT': '#FFFF99',   # Pastel Yellow
            'TDE': '#D8BFD8',     # Pastel Purple/Thistle
            'KN': '#B3FFFF',      # Pastel Cyan
            'GAP': '#FFCC80',     # Pastel Orange
            'Unknown': '#D3D3D3', # Light Gray
            'Other': '#C0C0C0'    # Silver
        }
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("GMM Cluster Selection")
        self.setMinimumSize(1100, 600)  # Set minimum size instead of fixed size
        self.resize(1200, 650)  # Initial size - smaller than before
        
        # Enable minimize, maximize, and close buttons (normal window behavior)
        self.setWindowFlags(
            QtCore.Qt.Dialog | 
            QtCore.Qt.WindowTitleHint | 
            QtCore.Qt.WindowSystemMenuHint | 
            QtCore.Qt.WindowMinMaxButtonsHint | 
            QtCore.Qt.WindowCloseButtonHint
        )
        
        # Apply modern styling (matching PySide6 theme)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #e2e8f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cbd5e1;
                background-color: white;
                selection-background-color: #dbeafe;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        
        # Main layout - vertical without header or footer
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Main content (horizontal split - 60% left, 40% right) - no header, no footer
        self._create_main_content(main_layout)
    
    def _create_main_content(self, layout):
        """Create main content with horizontal split layout (60/40 split with proper spacing)"""
        content_frame = QtWidgets.QFrame()
        content_layout = QtWidgets.QHBoxLayout(content_frame)
        content_layout.setContentsMargins(5, 5, 5, 5)  # Add margins to frame
        content_layout.setSpacing(8)  # Reduced spacing between panels
        
        # Left panel (60% width) - cluster selection and 3D plot
        self._create_left_panel(content_layout)
        
        # Right panel (40% width) - template matches
        self._create_right_panel(content_layout)
        
        layout.addWidget(content_frame)
    
    def _create_left_panel(self, layout):
        """Create left panel with cluster dropdown and 3D matplotlib plot"""
        self.left_panel = QtWidgets.QWidget()
        # Remove fixed width constraints to allow resizing
        left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        left_layout.setSpacing(10)  # Reduced spacing
        
        # Cluster selection dropdown
        selection_group = QtWidgets.QGroupBox("Select the best Type from GMM analysis")
        selection_layout = QtWidgets.QVBoxLayout(selection_group)
        selection_layout.setContentsMargins(10, 5, 10, 5)
        
        # Dropdown and button container (horizontal layout)
        dropdown_container = QtWidgets.QWidget()
        dropdown_layout = QtWidgets.QHBoxLayout(dropdown_container)
        dropdown_layout.setContentsMargins(0, 0, 0, 0)
        dropdown_layout.setSpacing(10)
        
        # Dropdown
        self.cluster_dropdown = QtWidgets.QComboBox()
        self.cluster_dropdown.setMaximumWidth(400)  # Limit dropdown width to prevent button cutoff
        self.cluster_dropdown.currentIndexChanged.connect(self._on_cluster_changed)
        dropdown_layout.addWidget(self.cluster_dropdown, 1)  # Take most space
        
        # Confirm button (smaller, inline with dropdown)
        confirm_btn = QtWidgets.QPushButton("Confirm")
        confirm_btn.setObjectName("confirm_btn")
        confirm_btn.clicked.connect(self._confirm_selection)
        confirm_btn.setDefault(True)
        dropdown_layout.addWidget(confirm_btn)
        
        selection_layout.addWidget(dropdown_container)
        
        left_layout.addWidget(selection_group)
        
        # 3D Plot area using matplotlib
        plot_group = QtWidgets.QGroupBox("📊 3D Cluster Visualization")
        plot_layout = QtWidgets.QVBoxLayout(plot_group)
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib 3D plot
            self._create_matplotlib_3d_plot(plot_layout)
        else:
            # Fallback message
            fallback = QtWidgets.QLabel(
                "📊 Matplotlib Required for 3D Clustering Visualization\n\n"
                "Install matplotlib to view interactive 3D cluster plots:\n\n"
                "pip install matplotlib\n\n"
                "Cluster selection is still available via the dropdown above."
            )
            fallback.setAlignment(QtCore.Qt.AlignCenter)
            fallback.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 12pt;")
            fallback.setWordWrap(True)
            fallback.setMinimumHeight(250)  # Smaller height for compact dialog
            plot_layout.addWidget(fallback)
        
        left_layout.addWidget(plot_group, 1)
        
        layout.addWidget(self.left_panel, 3)  # Give left panel 3 parts of space (60%)

        # Apply enhanced styles (after UI is built)
        try:
            from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
            self.button_manager = enhance_dialog_with_preset(self, 'cluster_selection_dialog')
        except Exception:
            pass
    
    def _create_matplotlib_3d_plot(self, layout):
        """Create matplotlib 3D scatter plot"""
        # Create matplotlib figure with white background
        self.fig = Figure(figsize=(8, 6), facecolor='white')  # Smaller initial size, will scale with window
        self.fig.patch.set_facecolor('white')
        
        # MAXIMIZE the plot area - use almost the entire window space
        self.fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.08)
        
        # Create 3D axes
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('white')
        
        # Create Qt canvas widget (parent will be managed by the layout/container)
        self.plot_widget = FigureCanvas(self.fig)
        self.plot_widget.setMinimumHeight(300)  # Smaller minimum height for initial size
        
        # Add canvas to layout
        layout.addWidget(self.plot_widget)
        
        # Connect matplotlib events for interactivity
        self.plot_widget.mpl_connect('pick_event', self._on_plot_pick)
    
    def _create_right_panel(self, layout):
        """Create right panel with template matches using matplotlib"""
        self.right_panel = QtWidgets.QWidget()
        # Remove fixed width constraints to allow resizing
        right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        right_layout.setSpacing(10)  # Reduced spacing
        
        # Top 2 matches panel
        matches_group = QtWidgets.QGroupBox("🔍 Top 2 Template Matches For Selected Cluster")
        matches_layout = QtWidgets.QVBoxLayout(matches_group)
        matches_layout.setContentsMargins(5, 5, 5, 5)
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure for matches
            self.matches_fig = Figure(figsize=(3.5, 5.5), dpi=100, facecolor='white')  # Even smaller to prevent label cutoff
            self.matches_fig.clear()
            
            # Create exactly 2 subplots vertically stacked
            self.matches_axes = []
            for i in range(2):
                ax = self.matches_fig.add_subplot(2, 1, i+1)
                ax.set_facecolor('white')
                ax.tick_params(colors='#666666', labelsize=10)
                for spine in ax.spines.values():
                    spine.set_color('#666666')
                ax.grid(True, alpha=0.3, linewidth=0.5)
                self.matches_axes.append(ax)
            
            # Optimize subplot parameters with more space for labels
            self.matches_fig.subplots_adjust(left=0.15, right=0.95, top=0.92, bottom=0.08, hspace=0.35)  # More space for labels
            
            # Embed in Qt widget
            self.matches_canvas = FigureCanvas(self.matches_fig)
            matches_layout.addWidget(self.matches_canvas)
        else:
            # Fallback text widget
            fallback_text = QtWidgets.QTextEdit()
            fallback_text.setReadOnly(True)
            fallback_text.setPlainText("Matplotlib required for template match visualization")
            matches_layout.addWidget(fallback_text)
        
        right_layout.addWidget(matches_group, 1)
        
        layout.addWidget(self.right_panel, 2)  # Give right panel 2 parts of space (40%)
    
    def _populate_data(self):
        """Populate dropdown and create 3D plot"""
        self._populate_dropdown()
        if MATPLOTLIB_AVAILABLE:
            self._plot_clusters()
    
    def _populate_dropdown(self):
        """Populate the cluster dropdown"""
        self.cluster_dropdown.clear()
        
        for idx, candidate in enumerate(self.all_candidates):
            cluster_type = candidate.get('type', 'Unknown')
            size = len(candidate.get('matches', []))
            
            # Get quality score
            quality = (
                candidate.get('penalized_score') or
                candidate.get('penalised_score') or
                candidate.get('composite_score') or
                candidate.get('mean_rlap') or 0.0
            )
            
            # Mark if this is the automatic best cluster
            is_best = (self.automatic_best is not None and candidate == self.automatic_best)
            best_mark = " 🏆" if is_best else ""
            
            item_text = f"#{idx+1}: {cluster_type} ({size} templates, Q={quality:.1f}){best_mark}"
            self.cluster_dropdown.addItem(item_text)
        
        # Set current selection
        if self.selected_index >= 0:
            self.cluster_dropdown.setCurrentIndex(self.selected_index)
    
    def _plot_clusters(self):
        """Plot clusters with 3D scatter plot"""
        if not MATPLOTLIB_AVAILABLE or not self.all_candidates:
            return
            
        # Preserve current view (especially azimuth) to avoid resetting angle on redraws
        try:
            current_azim = getattr(self.ax, 'azim', 45)
        except Exception:
            current_azim = 45

        self.ax.clear()
        self.scatter_plots.clear()
        self.scatter_to_index.clear()
        
        # Prepare type mapping with consistent ordering
        unique_types = sorted(list(set(c.get('type', 'Unknown') for c in self.all_candidates)))
        type_to_index = {sn_type: i for i, sn_type in enumerate(unique_types)}
        
        # Determine metric name (RLAP-CCC or RLAP)
        metric_name_global = 'RLAP'
        if MATH_UTILS_AVAILABLE:
            for cand in self.all_candidates:
                if cand.get('matches'):
                    metric_name_global = get_metric_name_for_match(cand['matches'][0])
                    break
        
        # Plot all clusters with enhanced styling
        for i, candidate in enumerate(self.all_candidates):
            matches = candidate.get('matches', [])
            if not matches:
                candidate_redshifts = [candidate.get('mean_redshift', 0)]
                if MATH_UTILS_AVAILABLE:
                    candidate_metrics = [candidate.get('mean_metric', candidate.get('mean_rlap', 0))]
                else:
                    candidate_metrics = [candidate.get('mean_rlap', 0)]
            else:
                candidate_redshifts = [m['redshift'] for m in matches]
                if MATH_UTILS_AVAILABLE:
                    candidate_metrics = [get_best_metric_value(m) for m in matches]
                else:
                    candidate_metrics = [m.get('rlap_ccc', m.get('rlap', 0)) for m in matches]
            
            candidate_type_indices = [type_to_index[candidate['type']]] * len(candidate_redshifts)
            
            # Visual style: consistent size, no transparency
            size = 30  # Slightly smaller points for better readability
            alpha = 1.0  # No transparency as requested
            
            # Gray edges for all by default (black edges added later for selected)
            edgecolor = 'gray'
            linewidth = 0.5
            
            # Use consistent type colors
            color = self.type_colors.get(candidate['type'], self.type_colors['Unknown'])
            
            # Plot all points
            scatter = self.ax.scatter(
                candidate_redshifts,
                candidate_type_indices,
                candidate_metrics,
                c=color,
                s=size,
                alpha=alpha,
                edgecolors=edgecolor,
                linewidths=linewidth,
                picker=5  # enable picking with 5px tolerance
            )
            
            self.scatter_plots.append((scatter, i, candidate))
            # Map this scatter artist to its cluster index for quick lookup on pick
            self.scatter_to_index[scatter] = i
        
        # Enhanced 3D setup
        self.ax.set_xlabel('Redshift (z)', color='#000000', fontsize=16, labelpad=15)
        self.ax.set_ylabel('SN Type', color='#000000', fontsize=16, labelpad=15)
        self.ax.set_zlabel(metric_name_global, color='#000000', fontsize=16, labelpad=15)
        self.ax.set_yticks(range(len(unique_types)))
        self.ax.set_yticklabels(unique_types, fontsize=12)
        
        # Set view and enable ONLY horizontal rotation, preserving current azimuth
        self.ax.view_init(elev=25, azim=current_azim)
        self.ax.set_box_aspect([2.5, 1.0, 1.5])
        
        # Enhanced 3D styling with completely white background
        try:
            # Ensure all panes are white and remove any blue artifacts
            self.ax.xaxis.pane.fill = True
            self.ax.yaxis.pane.fill = True
            self.ax.zaxis.pane.fill = True
            self.ax.xaxis.pane.set_facecolor('white')
            self.ax.yaxis.pane.set_facecolor('white')
            self.ax.zaxis.pane.set_facecolor('white')
            self.ax.xaxis.pane.set_edgecolor('lightgray')
            self.ax.yaxis.pane.set_edgecolor('lightgray')
            self.ax.zaxis.pane.set_edgecolor('lightgray')
            self.ax.xaxis.pane.set_alpha(1.0)
            self.ax.yaxis.pane.set_alpha(1.0)
            self.ax.zaxis.pane.set_alpha(1.0)
        except Exception as e:
            _LOGGER.warning(f"Some 3D styling options not available: {e}")
        
        # Enhanced plot styling
        self.ax.xaxis.label.set_color('#000000')
        self.ax.yaxis.label.set_color('#000000')
        self.ax.zaxis.label.set_color('#000000')
        self.ax.tick_params(colors='#666666', labelsize=12)
        self.ax.grid(True, alpha=0.4, color='gray', linestyle='-', linewidth=0.5)
        
        # Connect rotation constraint to ONLY allow horizontal (azimuth) rotation
        def on_rotate(event):
            if event.inaxes == self.ax:
                # LOCK elevation to 25 degrees, only allow azimuth changes (horizontal rotation only)
                self.ax.view_init(elev=25, azim=self.ax.azim)
                self.plot_widget.draw_idle()
        
        self.plot_widget.mpl_connect('motion_notify_event', on_rotate)
        
        # Show persistent highlight for the auto-selected best cluster
        if self.selected_cluster is not None and self.selected_index >= 0:
            self._add_persistent_highlight(self.selected_index)
        
        self.plot_widget.draw()
    
    def _add_persistent_highlight(self, cluster_index):
        """Add persistent highlight for selected cluster"""
        try:
            if MATH_UTILS_AVAILABLE:
                get_best_metric_value_local = get_best_metric_value
            else:
                get_best_metric_value_local = lambda m: m.get('rlap_ccc', m.get('rlap', 0))

            if 0 <= cluster_index < len(self.scatter_plots):
                scatter, idx, candidate = self.scatter_plots[cluster_index]
                
                # Add BLACK edge highlights to this cluster
                matches = candidate.get('matches', [])
                if not matches:
                    candidate_redshifts = [candidate.get('mean_redshift', 0)]
                    candidate_metrics = [candidate.get('mean_metric', candidate.get('mean_rlap', 0))]
                else:
                    candidate_redshifts = [m['redshift'] for m in matches]
                    candidate_metrics = [get_best_metric_value_local(m) for m in matches]
                
                unique_types = sorted(list(set(c.get('type', 'Unknown') for c in self.all_candidates)))
                type_to_index = {sn_type: i for i, sn_type in enumerate(unique_types)}
                candidate_type_indices = [type_to_index[candidate['type']]] * len(candidate_redshifts)
                
                # Add highlighted scatter with BLACK edges
                # Add highlighted scatter with picking disabled (so picks map to the base scatter only)
                highlight_scatter = self.ax.scatter(
                    candidate_redshifts,
                    candidate_type_indices,
                    candidate_metrics,
                    c=self.type_colors.get(candidate['type'], self.type_colors['Unknown']),
                    s=40,
                    alpha=1.0,
                    edgecolors='black',
                    linewidths=1.2,
                    zorder=3,
                    picker=False
                )
                
        except Exception as e:
            _LOGGER.debug(f"Error adding persistent highlight: {e}")
    
    def _on_plot_pick(self, event):
        """Handle matplotlib pick events to support left-click selection of clusters"""
        try:
            # Ensure this came from a mouse event and is a left-click
            mouse_event = getattr(event, 'mouseevent', None)
            if mouse_event is None or mouse_event.button != 1:
                return

            artist = getattr(event, 'artist', None)
            if artist is None:
                return

            # If the picked artist corresponds to a cluster scatter, select that cluster
            cluster_index = self.scatter_to_index.get(artist)
            if cluster_index is None:
                return

            self._select_cluster(cluster_index)
        except Exception as pick_err:
            _LOGGER.debug(f"Pick handling error: {pick_err}")
    
    def _on_cluster_changed(self, index):
        """Handle cluster dropdown selection change"""
        if 0 <= index < len(self.all_candidates):
            self._select_cluster(index)
    
    def _select_cluster(self, cluster_index):
        """Select a cluster and update UI"""
        if 0 <= cluster_index < len(self.all_candidates):
            self.selected_cluster = self.all_candidates[cluster_index]
            self.selected_index = cluster_index
            
            # Update dropdown
            self.cluster_dropdown.setCurrentIndex(cluster_index)
            
            # Clear and add highlights  
            if MATPLOTLIB_AVAILABLE:
                self._plot_clusters()  # Redraw plot with selection
            
            # Update matches panel
            self._update_matches_panel()
            
            _LOGGER.info(f"🎯 Selected cluster {cluster_index + 1}: {self.selected_cluster.get('type', 'Unknown')}")
    
    def _update_matches_panel(self):
        """Update the template matches panel"""
        if not MATPLOTLIB_AVAILABLE or not self.matches_canvas or not self.selected_cluster:
            return
        
        # Get top 2 matches from selected cluster
        if MATH_UTILS_AVAILABLE:
            matches = sorted(self.selected_cluster.get('matches', []), 
                            key=get_best_metric_value, reverse=True)[:2]
        else:
            matches = sorted(self.selected_cluster.get('matches', []), 
                            key=lambda m: m.get('rlap', 0), reverse=True)[:2]
        
        # Get input spectrum data
        input_wave = input_flux = None
        if (self.snid_result is not None and hasattr(self.snid_result, 'processed_spectrum') and
                self.snid_result.processed_spectrum):
            # Try different keys for processed spectrum
            if 'log_wave' in self.snid_result.processed_spectrum:
                input_wave = self.snid_result.processed_spectrum['log_wave']
                input_flux = self.snid_result.processed_spectrum['log_flux']
            elif 'wave' in self.snid_result.processed_spectrum:
                input_wave = self.snid_result.processed_spectrum['wave']
                input_flux = self.snid_result.processed_spectrum['flux']
        elif (self.snid_result is not None and hasattr(self.snid_result, 'input_spectrum') and
              isinstance(self.snid_result.input_spectrum, dict)):
            input_wave = self.snid_result.input_spectrum.get('wave')
            input_flux = self.snid_result.input_spectrum.get('flux')
        
        # Clear all axes first
        for i, ax in enumerate(self.matches_axes):
            if ax is not None:
                ax.clear()
                ax.set_facecolor('white')
                ax.spines['top'].set_visible(True)
                ax.spines['right'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
                ax.spines['left'].set_visible(True)
        
        # Update exactly 2 subplots
        for idx in range(2):
            if idx >= len(self.matches_axes):
                break
                
            ax = self.matches_axes[idx]
            if ax is None:
                continue
                
            ax.set_facecolor('white')
            ax.tick_params(colors='#666666', labelsize=9)
            for spine in ax.spines.values():
                spine.set_color('#666666')
            ax.grid(True, alpha=0.3, linewidth=0.5)
            
            if idx < len(matches) and matches[idx]:
                match = matches[idx]
                
                # Plot input spectrum (matching tkinter)
                if input_wave is not None and input_flux is not None:
                    ax.plot(input_wave, input_flux, color='#0078d4', linewidth=1.0, alpha=0.8, 
                           label='Input Spectrum', zorder=2)
                
                # Plot template match (matching tkinter)
                try:
                    # Try different ways to access template spectrum
                    t_wave = t_flux = None
                    
                    if 'spectra' in match and isinstance(match['spectra'], dict):
                        if 'flux' in match['spectra']:
                            t_wave = match['spectra']['flux'].get('wave')
                            t_flux = match['spectra']['flux'].get('flux')
                        elif 'wave' in match['spectra']:
                            t_wave = match['spectra']['wave']
                            t_flux = match['spectra']['flux']
                    elif 'wave' in match:
                        t_wave = match['wave']
                        t_flux = match['flux']
                    elif 'template_wave' in match:
                        t_wave = match['template_wave']
                        t_flux = match['template_flux']
                    
                    if t_wave is not None and t_flux is not None:
                        # Clean template name to remove _epoch_X suffix
                        template_name = clean_template_name(match.get('name', 'Unknown'))
                        ax.plot(t_wave, t_flux, color='#E74C3C', linewidth=1.0, alpha=0.9,
                               label=f"Template: {template_name}", zorder=3)
                        
                except Exception as e:
                    _LOGGER.debug(f"Error plotting template match {idx+1}: {e}")
                
                # Simplified title (matching tkinter)
                template_name = clean_template_name(match.get('name', 'Unknown'))
                # Use best available metric (RLAP-CCC if available, otherwise RLAP)
                if MATH_UTILS_AVAILABLE:
                    best_metric_value = get_best_metric_value(match)
                    metric_name = get_metric_name_for_match(match)
                    title_text = f"#{idx+1}: {template_name} ({metric_name}: {best_metric_value:.1f})"
                else:
                    title_text = f"#{idx+1}: {template_name} (RLAP: {match.get('rlap', 0):.1f})"
                ax.set_title(title_text, fontsize=10, color='#000000', 
                           fontweight='bold', pad=5)
                
                # Add legend for first plot only to save space (matching tkinter)
                if idx == 0:
                    ax.legend(loc='upper right', fontsize=7, framealpha=0.9)
                    
            else:
                # No match available (matching tkinter)
                ax.text(0.5, 0.5, f'No Match #{idx+1}', transform=ax.transAxes,
                       ha='center', va='center', fontsize=12, 
                       color='#666666', style='italic')
                ax.set_title(f"#{idx+1}: No Template Available", fontsize=11, 
                           color='#666666')
            
            # Set labels (only for bottom plot to save space) (matching tkinter)
            if idx == 1:  # Always the last (2nd) plot
                ax.set_xlabel('Wavelength (Å)', fontsize=10, color='#666666')
            ax.set_ylabel('Flux', fontsize=9, color='#666666')
        
        # Refresh the canvas (matching tkinter)
        try:
            if hasattr(self, 'matches_canvas') and self.matches_canvas:
                self.matches_canvas.draw()
        except Exception as e:
            _LOGGER.error(f"Error refreshing matches canvas: {e}")
    
    def get_result(self):
        """Get the selected cluster result"""
        return self.selected_cluster, self.selected_index
    
    def _confirm_selection(self):
        """Confirm the current selection and automatically show results (matching old GUI behavior)"""
        if self.selected_cluster is None:
            QtWidgets.QMessageBox.warning(
                self, "No Selection", 
                "Please select a cluster first."
            )
            return
        
        # Call callback with the user-selected cluster
        if self.callback:
            self.callback(self.selected_cluster, self.selected_index)
        
        # Close the dialog
        self.accept()
        
        # Automatically show results dialog (matching old GUI behavior)
        # The callback will handle the analysis completion and result display
        # through the normal workflow, so we don't need to explicitly call show_results here
        # The app controller will automatically show results after cluster selection
    
    def _auto_select_and_close(self):
        """Auto-select best cluster and close"""
        _LOGGER.info("🤖 Dialog closed - automatically using best cluster")
        
        try:
            if self.automatic_best and self.callback:
                # Find index of automatic best
                auto_index = self._find_automatic_best_index()
                self.callback(self.automatic_best, auto_index)
            elif self.all_candidates and self.callback:
                # Fallback: use first cluster if no automatic best
                _LOGGER.info("No automatic best found, using first cluster")
                self.callback(self.all_candidates[0], 0)
            else:
                _LOGGER.warning("No clusters or callback available for automatic selection")
        except Exception as e:
            _LOGGER.error(f"Error in automatic cluster selection: {e}")
        
        self.reject()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self._auto_select_and_close()
        event.accept()


def show_cluster_selection_dialog(parent, clusters, snid_result=None, callback=None):
    """
    Show the cluster selection dialog.
    
    Args:
        parent: Parent window
        clusters: List of cluster candidates
        snid_result: Full SNID analysis result (for spectrum access)
        callback: Callback function for cluster selection
        
    Returns:
        Tuple of (selected_cluster, selected_index) or (None, -1) if cancelled
        Note: If callback is provided, it will be called immediately and this may return None
    """
    dialog = PySide6ClusterSelectionDialog(parent, clusters, snid_result, callback)
    
    # Show dialog - callback will be called automatically
    result = dialog.exec()
    
    # If no callback was provided, return the result for backward compatibility
    if callback is None:
        if result == QtWidgets.QDialog.Accepted:
            return dialog.get_result()
        else:
            # Return automatic best if available
            if dialog.automatic_best and clusters:
                auto_index = clusters.index(dialog.automatic_best) if dialog.automatic_best in clusters else 0
                return dialog.automatic_best, auto_index
            return None, -1
    else:
        # Callback was used, return None to indicate async handling
        return None, -1 