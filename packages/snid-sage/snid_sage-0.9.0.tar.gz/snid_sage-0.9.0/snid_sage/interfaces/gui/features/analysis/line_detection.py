"""
SNID SAGE - Line Detection and Galaxy Redshift Analysis
======================================================

Handles spectral line detection and automatic
galaxy redshift detection using SNID analysis with galaxy templates.
"""

import os
from PySide6 import QtWidgets
from snid_sage.snid.snid import preprocess_spectrum, run_snid_analysis
import numpy as np
import traceback

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.line_detection')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.line_detection')

# Import manual redshift dialog
try:
    from snid_sage.interfaces.gui.components.pyside6_dialogs import show_manual_redshift_dialog
except ImportError:
    _LOGGER.warning("Manual redshift dialog not available")
    show_manual_redshift_dialog = None


class LineDetectionController:
    """Controller for handling line detection and galaxy redshift analysis"""
    
    def __init__(self, parent_gui):
        """Initialize line detection controller
        
        Parameters:
        -----------
        parent_gui : ModernSNIDSageGUI
            Reference to the main GUI instance
        """
        self.gui = parent_gui
        

        
    def auto_detect_and_compare_lines(self):
        """Auto-detect spectral lines in the current spectrum"""
        try:
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results:
                QtWidgets.QMessageBox.warning(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                              "No Data", "Please run SNID analysis first to detect lines.")
                return
            # Remove temporary placeholder: no-op for now
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                           "Line Detection Error", f"Failed to run line detection: {str(e)}")
    
    def search_nist_for_lines(self):
        """Search NIST database for spectral lines (removed in new GUI)"""
        # Functionality removed in the new GUI
        return
    
    def clear_line_markers(self):
        """Clear all line markers from the plot"""
        try:
            _LOGGER.debug("Clearing line markers...")
            # Clear markers and refresh plot
            if hasattr(self.gui, 'line_markers'):
                self.gui.line_markers.clear()
            
            # Refresh the current view to remove markers
            if hasattr(self.gui, 'snid_results') and self.gui.snid_results:
                self.gui.refresh_current_view()
            
        except Exception as e:
            print(f"Error clearing line markers: {e}")
    
    def reset_line_detection(self):
        """Reset line detection controller state"""
        try:
            _LOGGER.debug("🔄 Resetting line detection controller state...")
            
            # Clear line markers
            self.clear_line_markers()
            
            # Reset any cached line detection data
            if hasattr(self.gui, 'detected_lines'):
                self.gui.detected_lines = None
            
            # Reset line detection parameters to defaults
            if hasattr(self, 'line_detection_params'):
                self.line_detection_params = {}
            
            # Clear any galaxy redshift results
            if hasattr(self.gui, 'galaxy_redshift_result'):
                self.gui.galaxy_redshift_result = None
            
            # Reset any NIST search results
            if hasattr(self, 'nist_search_results'):
                self.nist_search_results = None
            
            _LOGGER.debug("Line detection controller state reset")
            
        except Exception as e:
            print(f"❌ Error resetting line detection controller: {e}")
    
    def open_combined_redshift_selection(self):
        """Open the combined redshift selection dialog with both manual and automatic options"""
        if not show_manual_redshift_dialog:
            QtWidgets.QMessageBox.critical(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                           "Feature Unavailable",
                                           "Manual redshift dialog is not available.\nPlease check your installation.")
            return
        
        if not self.gui.file_path:
            QtWidgets.QMessageBox.warning(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                          "No Spectrum", "Please load a spectrum first.")
            return
        
        try:
            _LOGGER.info("🌌 Starting combined redshift selection...")



            # Get current spectrum data 
            spectrum_data = self._get_current_spectrum_data()
            if not spectrum_data:
                QtWidgets.QMessageBox.critical(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                               "Spectrum Error",
                                               "Could not access current spectrum data.")
                return

            # Get current redshift estimate if available
            current_redshift = 0.0
            if hasattr(self.gui, 'params') and 'redshift' in self.gui.params:
                try:
                    current_redshift = float(self.gui.params['redshift'])
                except (ValueError, TypeError):
                    current_redshift = 0.0

            # Show enhanced manual redshift dialog with auto search capability
            # Using exactly the same approach as preprocessing dialog - no theme interactions
            result_redshift = show_manual_redshift_dialog(
                parent=self.gui.master,
                spectrum_data=spectrum_data,
                current_redshift=current_redshift,
                include_auto_search=True,  # Enable auto search functionality
                auto_search_callback=self._perform_automatic_redshift_search  # Callback for auto search
            )

            if result_redshift is not None:
                # Handle both old float format and new dict format
                if isinstance(result_redshift, dict):
                    # New format with mode information
                    redshift_value = result_redshift['redshift']
                    mode = result_redshift.get('mode', 'search')
                    forced_redshift = result_redshift.get('forced_redshift')
                    search_range = result_redshift.get('search_range', 0.01)  # Default to 0.01 if not specified

                    # Apply redshift configuration to analysis controller
                    if hasattr(self.gui, 'analysis_controller'):
                        if mode == 'force':
                            self.gui.analysis_controller.redshift_config.update({
                                'mode': 'forced',
                                'forced_redshift': forced_redshift
                            })
                            _LOGGER.info(f"Manual redshift applied with FORCED mode: z = {forced_redshift:.6f}")
                        else:
                            self.gui.analysis_controller.redshift_config.update({
                                'mode': 'automatic',
                                'forced_redshift': None,
                                'search_range': search_range
                            })
                            _LOGGER.info(f"Manual redshift applied with SEARCH mode: z = {redshift_value:.6f} ±{search_range:.6f}")

                    self._apply_manual_redshift(redshift_value, result_redshift)
                else:
                    # Old format - just a float redshift value (backward compatibility)
                    self._apply_manual_redshift(result_redshift)
                    _LOGGER.info(f"Manual redshift applied: z = {result_redshift:.6f}")
            else:
                _LOGGER.info("Redshift selection cancelled")



        except Exception as e:
            _LOGGER.error(f"Error in combined redshift selection: {e}")
            QtWidgets.QMessageBox.critical(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                           "Redshift Selection Error",
                                           f"Failed to start redshift selection:\n{str(e)}")
    
    def _perform_automatic_redshift_search(self, progress_callback=None):
        """Perform automatic redshift search using already preprocessed spectrum"""
        try:
            if progress_callback:
                progress_callback("Initializing automatic redshift search...")
            
            # Import necessary modules  
            from snid_sage.snid.snid import run_snid_analysis
            import os
            import numpy as np
            
            # Check for preprocessed spectrum first (new workflow)
            if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum is not None:
                if progress_callback:
                    progress_callback("Using preprocessed spectrum for galaxy template correlation...")
                
                # Use the flattened, tapered spectrum for correlation (like actual SNID)
                processed = self.gui.processed_spectrum
                
                # Get the spectrum ready for FFT correlation
                if 'tapered_flux' in processed:
                    tapered_flux = processed['tapered_flux']
                    spectrum_source = "tapered_flux (apodized flattened)"
                elif 'display_flat' in processed:
                    tapered_flux = processed['display_flat'] 
                    spectrum_source = "display_flat (flattened)"
                elif 'flat_flux' in processed:
                    tapered_flux = processed['flat_flux']
                    spectrum_source = "flat_flux (flattened)"
                else:
                    _LOGGER.error("No flattened spectrum data available for correlation")
                    if progress_callback:
                        progress_callback("Error: No flattened spectrum data available")
                    return {'success': False, 'error': 'No flattened spectrum data available for correlation'}
                
                log_wave = processed.get('log_wave')
                
                if log_wave is None or tapered_flux is None:
                    _LOGGER.error("Missing wavelength or flux data in preprocessed spectrum")
                    if progress_callback:
                        progress_callback("Error: Missing wavelength or flux data")
                    return {'success': False, 'error': 'Missing wavelength or flux data in preprocessed spectrum'}
                
                _LOGGER.info(f"🔍 Auto redshift search: Using {spectrum_source}")
                _LOGGER.info(f"🔍 Spectrum length: {len(tapered_flux)} points")
                
                # Create input spectrum tuple for SNID analysis
                input_spectrum = (log_wave, tapered_flux)
                
                if progress_callback:
                    progress_callback("Running galaxy template correlation analysis...")
                
                # Run SNID analysis with ONLY galaxy templates and NO preprocessing
                try:
                    # Get templates directory from GUI
                    templates_dir = self.gui.get_templates_dir()
                    if not templates_dir or not os.path.exists(templates_dir):
                        raise Exception("Templates directory not found")
                    
                    # Use the correct parameters for run_snid_analysis
                    results, analysis_trace = run_snid_analysis(
                        processed_spectrum=processed,  # Use the processed spectrum dict directly
                        templates_dir=templates_dir,
                        # Template filtering - galaxy types only
                        type_filter=['Galaxy'],  # Use Galaxy template type
                        # Analysis parameters
                        zmin=0.0,
                        zmax=1.0,
                        # Correlation parameters
                        rlapmin=3.0,  # Lower threshold for galaxy detection
                        lapmin=0.2,   # Lower overlap requirement for galaxies
                        peak_window_size=20,
                        # Output control
                        max_output_templates=15,
                        verbose=False,
                        show_plots=False,
                        save_plots=False
                    )
                    
                    if progress_callback:
                        progress_callback("Analysis complete - processing results...")
                    
                    if results and hasattr(results, 'best_matches') and results.best_matches:
                        # Filter for galaxy matches
                        galaxy_matches = []
                        _LOGGER.info(f"🔍 Processing {len(results.best_matches)} template matches for galaxy filtering")
                        
                        for i, match in enumerate(results.best_matches):
                            try:
                                if not isinstance(match, dict):
                                    _LOGGER.warning(f"⚠️ Match {i} is not a dictionary: {type(match)}")
                                    continue
                                    
                                # Get template information from the match
                                template = match.get('template', {})
                                if not isinstance(template, dict):
                                    _LOGGER.warning(f"⚠️ Template in match {i} is not a dictionary: {type(template)}")
                                    continue
                                    
                                template_type = template.get('type', '').lower()
                                template_name = template.get('name', '').lower()
                                
                                # Look for galaxy templates by type or name patterns
                                if (template_type in ['galaxy', 'gal'] or 
                                    template_name.startswith('kc') or 'gal' in template_name):
                                    
                                    # Create a simplified match structure for the redshift dialog
                                    galaxy_match = {
                                        'template_name': template.get('name', 'Unknown'),
                                        'template_type': template.get('type', 'Unknown'),
                                        'redshift': match.get('redshift', 0.0),
                                        'redshift_error': match.get('redshift_error', 0.0),
                                        'rlap': match.get('rlap', 0.0),
                                        'confidence': 'High' if match.get('rlap', 0.0) >= 8.0 else 
                                                     'Medium' if match.get('rlap', 0.0) >= 5.0 else 'Low'
                                    }
                                    galaxy_matches.append(galaxy_match)
                                    _LOGGER.debug(f"Added galaxy match: {galaxy_match['template_name']} (RLAP: {galaxy_match['rlap']:.2f})")
                                    
                            except Exception as match_error:
                                _LOGGER.error(f"❌ Error processing match {i}: {match_error}")
                                _LOGGER.error(f"   Match data: {match}")
                                continue
                        
                        _LOGGER.info(f"Found {len(galaxy_matches)} galaxy template matches")
                        
                        if galaxy_matches:
                            try:
                                # Sort by best available metric (RLAP-CCC if available, otherwise RLAP) - with extra validation
                                _LOGGER.debug("🔄 Sorting galaxy matches by best metric...")
                                try:
                                    from snid_sage.shared.utils.math_utils import get_best_metric_value
                                    galaxy_matches.sort(key=lambda x: get_best_metric_value(x) if isinstance(x, dict) else 0, reverse=True)
                                except ImportError:
                                    galaxy_matches.sort(key=lambda x: x.get('rlap_ccc', x.get('rlap', 0)) if isinstance(x, dict) else 0, reverse=True)
                                _LOGGER.debug("Successfully sorted galaxy matches")
                                
                                # Get the best match for the dialog
                                best_match = galaxy_matches[0]
                                
                                # Return the format expected by the manual redshift dialog
                                return {
                                    'success': True,
                                    'redshift': best_match['redshift'],
                                    'rlap': best_match['rlap'],
                                    'template': best_match['template_name'],
                                    'confidence': best_match['confidence'],
                                    'all_matches': galaxy_matches[:10]  # Include all matches for reference
                                }
                                
                            except Exception as sort_error:
                                _LOGGER.error(f"Error sorting galaxy matches: {sort_error}")
                                _LOGGER.error(f"   Galaxy matches: {galaxy_matches}")
                                # Return the best unsorted match if sorting fails
                                if galaxy_matches:
                                    best_match = galaxy_matches[0]
                                    return {
                                        'success': True,
                                        'redshift': best_match['redshift'],
                                        'rlap': best_match['rlap'],
                                        'template': best_match['template_name'],
                                        'confidence': best_match['confidence'],
                                        'all_matches': galaxy_matches[:10]
                                    }
                                else:
                                    return {'success': False, 'error': 'No valid galaxy matches found'}
                        else:
                            _LOGGER.warning("⚠️ No galaxy templates found after filtering")
                            return {'success': False, 'error': 'No galaxy templates found after filtering'}
                    else:
                        _LOGGER.warning("⚠️ No template matches found in SNID results")
                        return {'success': False, 'error': 'No template matches found in SNID results'}
                        
                except Exception as e:
                    _LOGGER.error(f"SNID analysis failed: {e}")
                    if progress_callback:
                        progress_callback(f"Analysis failed: {str(e)}")
                    return {'success': False, 'error': f'SNID analysis failed: {str(e)}'}
            
            # Fallback: No preprocessed spectrum available
            else:
                _LOGGER.error("No preprocessed spectrum available for automatic redshift search")
                _LOGGER.error("Please run preprocessing first before using automatic redshift search")
                if progress_callback:
                    progress_callback("Error: No preprocessed spectrum available. Run preprocessing first.")
                return {'success': False, 'error': 'No preprocessed spectrum available. Run preprocessing first.'}
                
        except Exception as e:
            _LOGGER.error(f"Automatic redshift search failed: {e}")
            _LOGGER.error(f"   Exception details: {traceback.format_exc()}")
            if progress_callback:
                progress_callback(f"Search failed: {str(e)}")
            return {'success': False, 'error': f'Automatic redshift search failed: {str(e)}'}
    
    def _get_current_spectrum_data(self):
        """Get the current spectrum data for manual redshift determination"""
        try:
            # PRIORITY 1: Try to get preprocessed FLATTENED spectrum data (new workflow)
            if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum is not None:
                processed = self.gui.processed_spectrum
                
                # Get the flattened spectrum data (continuum-removed) like the main GUI
                if 'log_wave' in processed:
                    log_wave = processed['log_wave']
                    
                    # Use display_flat if available (best quality flattened), otherwise fall back to flat_flux
                    if 'display_flat' in processed:
                        flat_flux = processed['display_flat']
                        spectrum_type = 'display_flat (continuum-removed)'
                    elif 'flat_flux' in processed:
                        flat_flux = processed['flat_flux']
                        spectrum_type = 'flat_flux (continuum-removed)'
                    else:
                        _LOGGER.error("No flattened spectrum data available in processed_spectrum")
                        return None
                    
                    # Apply zero-region filtering like the main GUI
                    filtered_wave, filtered_flux = self._filter_nonzero_spectrum(
                        log_wave, flat_flux, processed
                    )
                    
                    if filtered_wave is not None and filtered_flux is not None and len(filtered_wave) > 0:
                        _LOGGER.info(f"🎯 Redshift dialog: Using preprocessed flattened spectrum ({spectrum_type})")
                        _LOGGER.info(f"🎯 Wavelength range: {filtered_wave.min():.1f} - {filtered_wave.max():.1f} Å")
                        _LOGGER.info(f"🎯 Data points: {len(filtered_wave)} (zero-padding removed)")
                        
                        return {
                            'wavelength': filtered_wave,
                            'flux': filtered_flux,
                            'source': 'preprocessed_spectrum',
                            'spectrum_type': spectrum_type
                        }
            
            # PRIORITY 2: Try original spectrum (before preprocessing)
            if hasattr(self.gui, 'original_wave') and hasattr(self.gui, 'original_flux'):
                if self.gui.original_wave is not None and self.gui.original_flux is not None:
                    _LOGGER.info(f"🎯 Redshift dialog: Using original spectrum for display")
                    _LOGGER.info(f"🎯 Wavelength range: {self.gui.original_wave.min():.1f} - {self.gui.original_wave.max():.1f} Å")
                    
                    return {
                        'wavelength': self.gui.original_wave,
                        'flux': self.gui.original_flux,
                        'source': 'original_spectrum',
                        'spectrum_type': 'original'
                    }
            
            # PRIORITY 3: No spectrum data available
            _LOGGER.error("No spectrum data available for redshift dialog")
            return None
            
        except Exception as e:
            _LOGGER.error(f"Error getting spectrum data: {e}")
            _LOGGER.error(f"   Exception details: {traceback.format_exc()}")
            return None
    
    def _apply_manual_redshift(self, redshift: float, mode_result=None):
        """Apply manually determined redshift"""
        try:
            # Update SNID parameters with manual redshift
            self.gui.params['redshift'] = redshift
            
            # Store galaxy redshift result
            if mode_result and isinstance(mode_result, dict):
                self.gui.galaxy_redshift_result = {
                    'redshift': redshift,
                    'method': 'manual',
                    'confidence': 'user_determined',
                    'mode_result': mode_result  # Store the complete result
                }
            else:
                self.gui.galaxy_redshift_result = {
                    'redshift': redshift,
                    'method': 'manual',
                    'confidence': 'user_determined'
                }
            
            # Update redshift entry field if it exists (skip tkinter-specific code in PySide6)
            if hasattr(self.gui, 'redshift_entry'):
                try:
                    # If redshift_entry is a Qt widget with setText
                    if hasattr(self.gui.redshift_entry, 'setText'):
                        self.gui.redshift_entry.setText(f"{redshift:.6f}")
                except Exception:
                    pass
            
            # Compose status text with additional context (range or forced)
            status_text = None

            # Determine if we are in FORCED mode
            is_forced = False
            forced_z = None
            search_range = None

            if hasattr(self.gui, 'analysis_controller'):
                ac_cfg = self.gui.analysis_controller.redshift_config
                is_forced = ac_cfg.get('mode') == 'forced'
                forced_z = ac_cfg.get('forced_redshift', redshift) if is_forced else None

            if is_forced:
                status_text = f"z = {forced_z:.6f} (forced)"
            else:
                # If range information is available from mode_result, include it
                if mode_result and isinstance(mode_result, dict):
                    search_range = mode_result.get('search_range', 0.01)
                else:
                    # Fall back to global analysis controller configuration if present
                    ac_obj = getattr(self.gui, 'analysis_controller', None)
                    if ac_obj:
                        search_range = ac_obj.redshift_config.get('search_range', 0.01)

                status_text = f"z = {redshift:.6f} ±{search_range:.6f}" if search_range is not None else f"z = {redshift:.6f}"

            # Update status label without accessing theme manager - use simple fixed colors
            if hasattr(self.gui, 'redshift_status_label'):
                self.gui.redshift_status_label.configure(
                    text=status_text,
                    fg=self.gui.theme_manager.get_color('text_primary') if hasattr(self.gui, 'theme_manager') else 'black'
                )
            
            # Trigger workflow state update without any theme operations
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator.set_redshift_determined()
            elif hasattr(self.gui, 'update_button_states'):
                # Fallback for safety if the workflow integrator is somehow
                # unavailable (should not happen in normal operation).
                self.gui.update_button_states()
            
            # Log the redshift application without disrupting themes
            _LOGGER.info(f"Manual redshift applied: z = {redshift:.6f}")
            
            
            
        except Exception as e:
            _LOGGER.error(f"Error applying manual redshift: {e}")
            QtWidgets.QMessageBox.critical(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                           "Error", f"Failed to apply redshift: {str(e)}")
    
    def _show_no_results_dialog(self, progress_window):
        """Show dialog when no galaxy results are found"""
        progress_window.destroy()
        
        # Show options including manual redshift determination using Qt
        msg = QtWidgets.QMessageBox(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None)
        msg.setWindowTitle("No Results")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(
            "No galaxy redshift matches found.\n\n"
            "This could mean:\n"
            "• The spectrum is not a galaxy\n"
            "• The redshift is outside the search range\n"
            "• The signal-to-noise is too low\n"
            "• Galaxy templates don't match this type\n\n"
            "Would you like to try manual redshift determination?"
        )
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        res = msg.exec()

        # Do not change existing redshift status label; lack of match is a normal condition
        
        if res == QtWidgets.QMessageBox.Yes:  # Yes - manual redshift
            self.open_combined_redshift_selection()
        elif res == QtWidgets.QMessageBox.Cancel:  # Cancel - show help
            QtWidgets.QMessageBox.information(self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
                                              "Try Different Parameters",
                                              "Suggestions for improving galaxy redshift detection:\n\n"
                                              "• Check if the spectrum is actually a galaxy\n"
                                              "• Try adjusting the redshift range (zmin/zmax)\n"
                                              "• Use different preprocessing parameters\n"
                                              "• Consider manual redshift determination\n"
                                              "• Check if the spectrum has sufficient quality")
    
    def _show_error_dialog(self, progress_window, error_msg):
        """Show dialog when an error occurs"""
        progress_window.destroy()
        
        # Show error with manual redshift option via Qt
        res = QtWidgets.QMessageBox.question(
            self.gui if isinstance(self.gui, QtWidgets.QWidget) else None,
            "Analysis Error",
            f"Galaxy redshift detection failed:\n\n{error_msg}\n\nWould you like to try manual redshift determination instead?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.Yes:
            self.open_combined_redshift_selection()
    
    def _show_results_dialog(self, progress_window, best_z, best_rlap, best_template, confidence, 
                            redshifts, rlaps, template_names, snid_result):
        """Show dialog with galaxy redshift results (Qt minimal dialog)"""
        progress_window.destroy()
        parent = self.gui if isinstance(self.gui, QtWidgets.QWidget) else None
        summary = (
            f"Redshift (z): {best_z:.6f}\n"
            f"Correlation (rlap): {best_rlap:.1f}\n"
            f"Template: {best_template}\n"
            f"Confidence: {confidence}%\n\n"
            f"Accept this redshift?"
        )
        msg = QtWidgets.QMessageBox(parent)
        msg.setWindowTitle("Galaxy Redshift Results")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(summary)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        msg.button(QtWidgets.QMessageBox.Yes).setText("Accept")
        msg.button(QtWidgets.QMessageBox.No).setText("Manual...")
        msg.button(QtWidgets.QMessageBox.Cancel).setText("Close")
        res = msg.exec()

        if res == QtWidgets.QMessageBox.Yes:
            # Update any redshift-related parameters
            self.gui.params['redshift'] = best_z

            # Update redshift status label
            if hasattr(self.gui, 'redshift_status_label'):
                try:
                    self.gui.redshift_status_label.setText(f"✅ z = {best_z:.6f} (auto, rlap {best_rlap:.1f})")
                except Exception:
                    pass

            # Store auto redshift result
            self.gui.galaxy_redshift_result = {
                'redshift': best_z,
                'method': 'auto',
                'confidence': confidence,
                'rlap': best_rlap,
                'template': best_template
            }

            QtWidgets.QMessageBox.information(
                parent,
                "Redshift Accepted",
                (
                    f"Galaxy redshift z = {best_z:.6f} has been set.\n\n"
                    f"SNID analysis will now search in a tight range around this redshift.\n"
                    f"Search range: z = {max(-0.01, best_z-0.05):.6f} to {best_z+0.05:.6f}"
                )
            )
        elif res == QtWidgets.QMessageBox.No:
            self.open_combined_redshift_selection()
    
    def _safe_float(self, value, default=0.0):
        """Safely convert value to float"""
        try:
            return float(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value, default=0):
        """Safely convert value to int"""
        try:
            return int(float(value)) if value else default
        except (ValueError, TypeError):
            return default
    
    def _safe_bool(self, value, default=False):
        """Safely convert value to bool"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value) if value is not None else default 

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _ensure_flat_view_active(self):
        """Guarantee that the GUI remains in 'Flat' view and refresh the segmented buttons."""
        try:
            if hasattr(self.gui, 'view_style') and self.gui.view_style:
                if self.gui.view_style.get() != "Flat":
                    self.gui.view_style.set("Flat")
                # Always refresh colours
                if hasattr(self.gui, '_update_segmented_control_buttons'):
                    self.gui._update_segmented_control_buttons()
        except Exception:
            pass 
