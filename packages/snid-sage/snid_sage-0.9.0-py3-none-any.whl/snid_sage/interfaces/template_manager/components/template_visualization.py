"""
Template Visualization Widget
============================

Widget for visualizing template spectra with multiple view modes.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui

# Import flexible number input widget
from snid_sage.interfaces.gui.components.widgets.flexible_number_input import create_flexible_int_input

from .template_data import TemplateData

# Import layout manager
from ..utils.layout_manager import get_template_layout_manager

# PyQtGraph for high-performance plotting
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
    # Import enhanced plot widget
    from snid_sage.interfaces.gui.components.plots.enhanced_plot_widget import EnhancedPlotWidget
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    pg = None
    EnhancedPlotWidget = None

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.visualization')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.visualization')


class TemplateVisualizationWidget(QtWidgets.QWidget):
    """Widget for visualizing template spectra"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_template = None
        self.template_data = None
        self.plot_manager = None
        self.plot_widget = None
        self.layout_manager = get_template_layout_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the visualization interface"""
        layout = QtWidgets.QVBoxLayout(self)
        self.layout_manager.apply_panel_layout(self, layout)
        
        # Control panel
        control_panel = QtWidgets.QGroupBox("Visualization Controls")
        self.layout_manager.setup_group_box(control_panel)
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        
        self.view_mode_combo = QtWidgets.QComboBox()
        self.view_mode_combo.addItems(["All Epochs", "Individual Epoch"])
        self.view_mode_combo.currentTextChanged.connect(self.update_plot)
        
        self.epoch_selector = create_flexible_int_input(min_val=1, max_val=999, default=1)
        self.epoch_selector.valueChanged.connect(self.update_plot)
        
        control_layout.addWidget(QtWidgets.QLabel("View Mode:"))
        control_layout.addWidget(self.view_mode_combo)
        control_layout.addWidget(QtWidgets.QLabel("Epoch:"))
        control_layout.addWidget(self.epoch_selector)
        control_layout.addStretch()
        
        layout.addWidget(control_panel)
        
        # Plot area
        self.plot_widget = QtWidgets.QWidget()
        self.layout_manager.setup_template_viewer(self.plot_widget)
        self.plot_widget.setStyleSheet("background-color: white; border: 1px solid gray;")
        layout.addWidget(self.plot_widget)
        
        # Initialize PyQtGraph plotting
        self._setup_pyqtgraph_plot()
        
        # Template info panel - REMOVED as requested
        # The info panel has been removed to simplify the interface
        
    def _setup_pyqtgraph_plot(self):
        """Setup PyQtGraph plotting in the widget"""
        try:
            if not PYQTGRAPH_AVAILABLE:
                raise ImportError("PyQtGraph not available")
            
            # Configure PyQtGraph for software rendering
            pg.setConfigOptions(
                antialias=True, 
                useOpenGL=False,
                enableExperimental=False,
                background='w',
                foreground='k',
                exitCleanup=True,
                crashWarning=False
            )
            
            # Create enhanced PyQtGraph plot widget with save functionality
            self.plot_widget_pg = EnhancedPlotWidget()
            
            # Add to widget layout
            plot_layout = QtWidgets.QVBoxLayout(self.plot_widget)
            plot_layout.addWidget(self.plot_widget_pg)
            
            # Get plot item for customization
            self.plot_item = self.plot_widget_pg.getPlotItem()
            
            # Setup labels and grid
            self.plot_item.setLabel('left', 'Flux')
            self.plot_item.setLabel('bottom', 'Wavelength', units='Å')
            self.plot_item.showGrid(x=True, y=True, alpha=0.3)
            
            # Apply theme colors
            self._apply_pyqtgraph_theme()
            
            # Initial welcome message
            self._show_welcome_message()
            
        except ImportError as e:
            _LOGGER.warning(f"PyQtGraph not available: {e}")
            # Create placeholder
            placeholder = QtWidgets.QLabel("Plot visualization requires PyQtGraph\n\npip install pyqtgraph")
            placeholder.setAlignment(QtCore.Qt.AlignCenter)
            placeholder.setStyleSheet("background-color: #f0f0f0; padding: 50px; color: gray;")
            plot_layout = QtWidgets.QVBoxLayout(self.plot_widget)
            plot_layout.addWidget(placeholder)
            
    def _apply_pyqtgraph_theme(self):
        """Apply theme colors to PyQtGraph plot"""
        if not hasattr(self, 'plot_item'):
            return
            
        try:
            # Set background and foreground colors
            self.plot_item.getViewBox().setBackgroundColor('#ffffff')
            
            # Set axis colors
            for axis in ['left', 'bottom']:
                ax = self.plot_item.getAxis(axis)
                ax.setPen(pg.mkPen(color='black', width=1))
                ax.setTextPen(pg.mkPen(color='black'))
                
        except Exception as e:
            _LOGGER.warning(f"Could not apply PyQtGraph theme: {e}")
            
    def _show_welcome_message(self):
        """Show welcome message on empty plot"""
        if not hasattr(self, 'plot_item'):
            return
            
        # Add text item for welcome message
        text_item = pg.TextItem('Select a template to view its spectrum', 
                               color='gray', anchor=(0.5, 0.5))
        self.plot_item.addItem(text_item)
        
        # Position text in center
        text_item.setPos(5000, 0.5)  # Approximate center wavelength
            
    def set_template(self, template_name: str, template_info: Dict[str, Any]):
        """Set the current template to visualize"""
        self.current_template = {
            'name': template_name,
            'info': template_info
        }
        
        # Info labels removed - template information now shown only in plot title
        
        # Update epoch selector
        epochs = template_info.get('epochs', 1)
        # Use setRange instead of setMaximum for FlexibleNumberInput
        self.epoch_selector.setRange(1, epochs)
        
        # Load template data
        self._load_template_data()
        
        # Update plot
        self.update_plot()
        
    def _load_template_data(self):
        """Load template data from storage"""
        if not self.current_template:
            return
            
        try:
            template_info = self.current_template['info']
            storage_file = template_info.get('storage_file', '')
            
            if storage_file:
                # Find the full path to the storage file
                storage_path = self._find_storage_file(storage_file)
                if storage_path:
                    self.template_data = TemplateData(self.current_template['name'], template_info)
                    self.template_data.load_data(storage_path)
                else:
                    _LOGGER.warning(f"Storage file not found: {storage_file}")
                    # Create template data with mock data
                    self.template_data = TemplateData(self.current_template['name'], template_info)
                    self.template_data._create_mock_data()
            else:
                # Create template data with mock data
                self.template_data = TemplateData(self.current_template['name'], template_info)
                self.template_data._create_mock_data()
                    
        except Exception as e:
            _LOGGER.error(f"Error loading template data: {e}")
            # Create fallback data
            if self.current_template:
                self.template_data = TemplateData(self.current_template['name'], self.current_template['info'])
                self.template_data._create_mock_data()
            
    def _find_storage_file(self, storage_file: str) -> Optional[str]:
        """Find the full path to a storage file (packaged or user)."""
        # 1) Packaged templates directory via importlib.resources
        try:
            from importlib import resources
            with resources.as_file(resources.files('snid_sage') / 'templates' / storage_file) as p:
                if p.exists():
                    _LOGGER.info(f"Found storage file at: {p}")
                    return str(p)
        except Exception:
            pass

        # 2) User templates directory resolved by TemplateService
        try:
            from snid_sage.interfaces.template_manager.services.template_service import _USER_DIR  # type: ignore
            candidate = _USER_DIR / storage_file
            if candidate.exists():
                _LOGGER.info(f"Found storage file at: {candidate}")
                return str(candidate)
        except Exception:
            pass

        # 3) Legacy fallbacks
        for path in [
            os.path.join("snid_sage", "templates", storage_file),
            os.path.join("templates", storage_file),
            storage_file,
        ]:
            if os.path.exists(path):
                _LOGGER.info(f"Found storage file at: {path}")
                return path

        _LOGGER.warning(f"Storage file {storage_file} not found in any of the expected locations")
        return None
        
    def update_plot(self):
        """Update the plot based on current settings"""
        if not self.current_template:
            return
            
        try:
            if hasattr(self, 'plot_item'):
                self._plot_template_spectrum()
            else:
                self._create_placeholder_plot()
        except Exception as e:
            _LOGGER.error(f"Error updating plot: {e}")
            
    def _plot_template_spectrum(self):
        """Plot the actual template spectrum using PyQtGraph"""
        if not hasattr(self, 'plot_item'):
            return
            
        # Clear previous plots and legends
        self.plot_item.clear()
        # Explicitly clear legend if it exists
        if hasattr(self.plot_item, 'legend') and self.plot_item.legend is not None:
            self.plot_item.legend.scene().removeItem(self.plot_item.legend)
            self.plot_item.legend = None
        
        if self.template_data and self.template_data.wave_data is not None:
            view_mode = self.view_mode_combo.currentText()
            
            if view_mode == "All Epochs":
                self._plot_all_epochs_pg()
            elif view_mode == "Individual Epoch":
                self._plot_individual_epoch_pg()
            
        else:
            # Create a sample plot if no real data available
            self._create_sample_plot_pg()
            
        # Set title with comprehensive template information
        from snid_sage.shared.utils import clean_template_name
        clean_name = clean_template_name(self.current_template['name'])
        template_info = self.current_template['info']
        
        # Build comprehensive title
        title_parts = [f"Template: {clean_name}"]
        
        # Add type/subtype
        type_info = template_info.get('type', 'Unknown')
        subtype_info = template_info.get('subtype', '')
        if subtype_info and subtype_info != 'Unknown':
            type_info += f"/{subtype_info}"
        title_parts.append(f"Type: {type_info}")
        
        # Add age
        age = template_info.get('age', 'Unknown')
        title_parts.append(f"Age: {age} days")
        
        # Add epoch info if multiple epochs
        epochs = template_info.get('epochs', 1)
        if epochs > 1:
            title_parts.append(f"Epochs: {epochs}")
        
        title = " | ".join(title_parts)
        self.plot_item.setTitle(title)
        
    def _plot_all_epochs_pg(self):
        """Plot all epochs with vertical offset using PyQtGraph"""
        if not self.template_data or not self.template_data.epochs:
            return
            
        # Validate data
        if self.template_data.wave_data is None:
            _LOGGER.warning("No wavelength data available for plotting")
            return
            
        # Generate colors
        colors = [pg.intColor(i, len(self.template_data.epochs)) for i in range(len(self.template_data.epochs))]
        
        legend_items = []
        
        for i, epoch in enumerate(self.template_data.epochs):
            if epoch['flux'] is not None and len(epoch['flux']) == len(self.template_data.wave_data):
                # Apply vertical offset
                offset = i * 0.5
                flux = epoch['flux'] + offset
                age = epoch['age']
                
                # Create plot curve
                curve = self.plot_item.plot(
                    self.template_data.wave_data,
                    flux,
                    pen=pg.mkPen(color=colors[i], width=1.5),
                    name=f"Age: {age:.1f} days",
                    connect='all',
                    autoDownsample=False,
                    clipToView=False,
                    downsample=1,
                )
                legend_items.append((curve, f"Age: {age:.1f} days"))
            else:
                _LOGGER.warning(f"Skipping epoch {i}: flux data mismatch with wavelength grid")
        
        # Add legend - ensure no duplicates
        if legend_items:
            # Remove any existing legend first (already handled in _plot_template_spectrum)
            legend = self.plot_item.addLegend(offset=(10, 10))
            for curve, label in legend_items:
                legend.addItem(curve, label)
        
    def _plot_individual_epoch_pg(self):
        """Plot individual epoch using PyQtGraph"""
        if not self.template_data or not self.template_data.epochs:
            return
            
        # Validate data
        if self.template_data.wave_data is None:
            _LOGGER.warning("No wavelength data available for plotting")
            return
            
        epoch_value = self.epoch_selector.value()
        if epoch_value is None:
            epoch_value = 1  # Default to first epoch
        epoch_idx = int(epoch_value) - 1
        
        if epoch_idx < len(self.template_data.epochs):
            epoch = self.template_data.epochs[epoch_idx]
            if (epoch['flux'] is not None and 
                len(epoch['flux']) == len(self.template_data.wave_data)):
                age = epoch['age']
                
                # Plot the epoch
                curve = self.plot_item.plot(
                    self.template_data.wave_data,
                    epoch['flux'],
                    pen=pg.mkPen(color='blue', width=2),
                    name=f"Age: {age:.1f} days",
                    connect='all',
                    autoDownsample=False,
                    clipToView=False,
                    downsample=1,
                )
                
                # Add legend
                legend = self.plot_item.addLegend(offset=(10, 10))
                legend.addItem(curve, f"Age: {age:.1f} days")
            else:
                _LOGGER.warning(f"Epoch {epoch_idx}: flux data mismatch with wavelength grid")
        else:
            _LOGGER.warning(f"Epoch index {epoch_idx} out of range (available: {len(self.template_data.epochs)})")
                
    
        
    def _create_sample_plot_pg(self):
        """Create a sample plot when no real data is available using PyQtGraph"""
        wave = np.linspace(3000, 9000, 1000)
        flux = np.exp(-0.5 * ((wave - 5000) / 1000)**2) + 0.1 * np.random.normal(0, 1, 1000)
        
        # Plot sample data
        self.plot_item.plot(
            wave,
            flux,
            pen=pg.mkPen(color='blue', width=1.5),
            connect='all',
            autoDownsample=False,
            clipToView=False,
            downsample=1,
        )
        
        # Add text overlay
        text_item = pg.TextItem('Sample spectrum (real data not available)', 
                               color='red', anchor=(0.5, 0.1))
        self.plot_item.addItem(text_item)
        text_item.setPos(6000, np.max(flux) * 0.9)
            
    def _create_placeholder_plot(self):
        """Create a placeholder plot until template loading is implemented"""
        # This method is kept for compatibility but now handled by _plot_template_spectrum
        pass
    
    def clear_plot(self):
        """Clear the current plot"""
        if hasattr(self, 'plot_item'):
            self.plot_item.clear()
            self._show_welcome_message()
    
    def export_plot(self, filename: str):
        """Export the current plot to file"""
        if hasattr(self, 'plot_widget_pg'):
            try:
                exporter = pg.exporters.ImageExporter(self.plot_widget_pg.plotItem)
                exporter.export(filename)
                _LOGGER.info(f"Plot exported to {filename}")
            except Exception as e:
                _LOGGER.error(f"Error exporting plot: {e}")
    
    def get_current_template_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently displayed template"""
        if self.current_template and self.template_data:
            return self.template_data.get_metadata_summary()
        return None