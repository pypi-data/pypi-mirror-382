from PySide6 import QtWidgets


def create_options(dialog, layout: QtWidgets.QVBoxLayout) -> None:
    desc = QtWidgets.QLabel("Apply log-wavelength rebinning and optional flux scaling.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
    layout.addWidget(desc)

    rebin_group = QtWidgets.QGroupBox("Rebinning Configuration")
    rebin_layout = QtWidgets.QVBoxLayout(rebin_group)
    # Add more vertical spacing to increase the area
    rebin_layout.setSpacing(15)
    rebin_layout.setContentsMargins(15, 20, 15, 20)

    dialog.log_rebin_cb = QtWidgets.QCheckBox("Apply log-wavelength rebinning")
    dialog.log_rebin_cb.setChecked(True)
    dialog.log_rebin_cb.setEnabled(False)
    rebin_layout.addWidget(dialog.log_rebin_cb)

    dialog.flux_scaling_cb = QtWidgets.QCheckBox("Scale flux to mean value")
    dialog.flux_scaling_cb.setChecked(dialog.processing_params['flux_scaling'])
    dialog.flux_scaling_cb.toggled.connect(lambda *_: _on_flux_scaling_changed(dialog))
    rebin_layout.addWidget(dialog.flux_scaling_cb)

    # Add some extra vertical space at the bottom
    rebin_layout.addStretch(1)
    layout.addWidget(rebin_group)

    info_group = QtWidgets.QGroupBox("Grid Information")
    info_layout = QtWidgets.QVBoxLayout(info_group)
    # Add more vertical spacing to increase the area
    info_layout.setSpacing(15)
    info_layout.setContentsMargins(15, 20, 15, 20)
    
    try:
        from snid_sage.snid.snid import NW, MINW, MAXW
        info_text = QtWidgets.QLabel(
            f"Target grid: {NW} points\n"
            f"Wavelength range: {MINW} - {MAXW} Å\n"
            "Log spacing: uniform in log wavelength"
        )
    except Exception:
        info_text = QtWidgets.QLabel(
            "Target grid: 1024 points\nWavelength range: 2500 - 10000 Å\nLog spacing: uniform in log wavelength"
        )
    info_text.setStyleSheet("color: #64748b; font-size: 10pt;")
    info_layout.addWidget(info_text)
    
    # Add some extra vertical space at the bottom
    info_layout.addStretch(1)
    layout.addWidget(info_group)


def apply_step(dialog) -> None:
    scale_flux = True
    try:
        if hasattr(dialog, 'flux_scaling_cb') and dialog.flux_scaling_cb is not None:
            scale_flux = bool(dialog.flux_scaling_cb.isChecked())
    except Exception:
        pass
    dialog.preview_calculator.apply_step("log_rebin_with_scaling", scale_to_mean=scale_flux, step_index=2)


def calculate_preview(dialog):
    scale_to_mean = bool(dialog.processing_params.get('flux_scaling', True))
    return dialog.preview_calculator.preview_step("log_rebin_with_scaling", scale_to_mean=scale_to_mean)


def _on_flux_scaling_changed(dialog):
    dialog.processing_params['flux_scaling'] = dialog.flux_scaling_cb.isChecked()
    dialog._update_preview()


