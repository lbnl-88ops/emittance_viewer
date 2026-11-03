from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout, QFrame, 
    QCheckBox, QSlider, QSpinBox, QDoubleSpinBox, QGroupBox, QSizePolicy
)

from PyQt6.QtCore import Qt, pyqtSignal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from emittance_viewer.gui.style.constants import (
    COLOR_ACTION, COLOR_BG, COLOR_GRID, FONT_MONO, FONT_SANS, COLOR_TEXT
)
from emittance_viewer.gui.style.styles import TITLE_LABEL_STYLE, LABEL_STYLE
from emittance_viewer.plotting.emittance_by_cutoff import plot_emittance_by_cutoff

class DataField(QWidget):
    def __init__(self, label, value="N/A", unit="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_name = QLabel(f"{label}:")
        self.lbl_name.setStyleSheet(f"font-family: {FONT_SANS}; font-size: 11px;")
        layout.addWidget(self.lbl_name)
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_value.setStyleSheet(f"font-family: {FONT_MONO}; font-weight: bold; color: {COLOR_TEXT};")
        layout.addWidget(self.lbl_value)
        
        self.lbl_unit = QLabel(unit)
        self.lbl_unit.setStyleSheet(f"font-family: {FONT_SANS}; font-size: 10px; color: {COLOR_TEXT};")
        layout.addWidget(self.lbl_unit)

    def set_value(self, value):
        self.lbl_value.setText(str(value))

class SingleScanPane(QWidget):
    fittingChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # --- Beam Data ---
        self.beam_group = QGroupBox("Beam Data")
        self.beam_layout = QVBoxLayout(self.beam_group)
        self.field_beamline = DataField("Beamline")
        self.field_extraction_v = DataField("Extraction V", unit="kV")
        self.field_total_current = DataField("Total Current", unit="µA")
        self.field_utilization = DataField("Utilization", unit="%")
        self.beam_layout.addWidget(self.field_beamline)
        self.beam_layout.addWidget(self.field_extraction_v)
        self.beam_layout.addWidget(self.field_total_current)
        self.beam_layout.addWidget(self.field_utilization)
        self.layout.addWidget(self.beam_group)

        # --- Emittance Data ---
        self.emittance_group = QGroupBox("Emittance Data")
        self.emittance_layout = QVBoxLayout(self.emittance_group)
        self.field_rms_emit = DataField("4xRMS Emittance", unit="mm-mrad")
        self.field_norm_emit = DataField("Norm. Emittance", unit="mm-mrad")
        self.field_alpha = DataField("Alpha")
        self.field_beta = DataField("Beta", unit="mm/mrad")
        self.field_gamma = DataField("Gamma", unit="mrad/mm")
        self.field_x_centroid = DataField("x Centroid", unit="mm")
        self.field_xp_centroid = DataField("x' Centroid", unit="mrad")
        
        self.emittance_layout.addWidget(self.field_rms_emit)
        self.emittance_layout.addWidget(self.field_norm_emit)
        self.emittance_layout.addWidget(self.field_alpha)
        self.emittance_layout.addWidget(self.field_beta)
        self.emittance_layout.addWidget(self.field_gamma)
        self.emittance_layout.addWidget(self.field_x_centroid)
        self.emittance_layout.addWidget(self.field_xp_centroid)
        self.layout.addWidget(self.emittance_group)

        # --- Fitting Controls ---
        self.fitting_group = QGroupBox("Background subtraction")
        self.fitting_layout = QVBoxLayout(self.fitting_group)

        # Sigma Clip
        self.sigma_clip_enable = QCheckBox("Sigma Clip")
        self.sigma_clip_enable.setChecked(True)
        self.sigma_clip_enable.stateChanged.connect(self.fittingChanged.emit)
        self.fitting_layout.addWidget(self.sigma_clip_enable)

        sigma_layout = QHBoxLayout()
        sigma_layout.addWidget(QLabel("Alpha:"))
        self.sigma_alpha_spin = QSpinBox()
        self.sigma_alpha_spin.setRange(1, 10)
        self.sigma_alpha_spin.setValue(2)
        self.sigma_alpha_spin.valueChanged.connect(self.fittingChanged.emit)
        sigma_layout.addWidget(self.sigma_alpha_spin)
        self.fitting_layout.addLayout(sigma_layout)

        # Offset
        self.offset_enable = QCheckBox("Background Offset")
        self.offset_enable.setChecked(True)
        self.offset_enable.stateChanged.connect(self.fittingChanged.emit)
        self.fitting_layout.addWidget(self.offset_enable)

        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("Calc Value:"))
        self.lbl_offset_value = QLabel("0.00")
        self.lbl_offset_value.setStyleSheet(f"font-family: {FONT_MONO}; color: {COLOR_TEXT};")
        offset_layout.addWidget(self.lbl_offset_value)
        self.fitting_layout.addLayout(offset_layout)

        # Mini Plot for custom analysis/visualization
        self.mini_figure = Figure(figsize=(3, 2), dpi=100)
        self.mini_figure.patch.set_facecolor(COLOR_BG)
        self.mini_canvas = FigureCanvas(self.mini_figure)
        self.mini_canvas.setMinimumHeight(150)
        self.mini_ax = self.mini_figure.add_subplot(111)
        self.mini_ax.set_facecolor(COLOR_BG)
        self.mini_ax.tick_params(colors=COLOR_TEXT, labelsize=8)
        for spine in self.mini_ax.spines.values():
            spine.set_edgecolor(COLOR_GRID)
        
        self.fitting_layout.addWidget(self.mini_canvas)

        self.layout.addWidget(self.fitting_group)

        self.layout.addStretch()

        # Styling
        self.setStyleSheet(f"""
            QGroupBox {{ 
                font-family: {FONT_SANS}; 
                color: {COLOR_TEXT}; 
                font-weight: bold;
                border: 1px solid {COLOR_GRID}; 
                margin-top: 1.2ex; 
                padding-top: 10px;
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                left: 8px; 
                padding: 0 3px; 
            }}
            QLabel {{ font-family: {FONT_SANS}; color: {COLOR_TEXT}; }}
        """)

    def _set_field(self, field, value: float | str | None, format: str | None = None):
        value_to_set = "---"
        match value:
            case float():
                try:
                    value = float(value)
                    value_to_set = f"{value:{format}}"
                except ValueError:
                    value_to_set = "N/A"
            case str():
                value_to_set = value
        field.set_value(value_to_set)


    def update_data(self, data, rms_emittance, emittance_file):
        """Update fields with a dictionary of values"""
        data_to_update = {
            self.field_beamline: ["beamline", None],
            self.field_extraction_v: ["extraction_v", ".2f"],
            self.field_total_current: ["total_current", ".2f"],
            self.field_rms_emit: ['rms_emit', ".4f"],
            self.field_norm_emit: ['norm_emit', ".4f"],
            self.field_alpha: ['alpha', ".4f"],
            self.field_beta: ['beta', ".4f"],
            self.field_gamma: ['gamma', ".4f"],
            self.field_x_centroid: ['x_centroid', ".4f"],
            self.field_xp_centroid: ['xp_centroid', ".4f"],
        }

        for field, key in data_to_update.items():
            self._set_field(field, data[key[0]], key[1])

        if "utilization" in data:
            util = data["utilization"]
            self._set_field(self.field_utilization, data["utilization"], ".0f")
            # self.field_utilization.set_value(f"{util:.0f}%")
            if util is not None and util < 10:
                self.field_utilization.lbl_value.setStyleSheet(f"font-family: {FONT_MONO}; font-weight: bold; color: {COLOR_ACTION};")
            else:
                self.field_utilization.lbl_value.setStyleSheet(f"font-family: {FONT_MONO}; font-weight: bold; color: {COLOR_TEXT};")
        
        if "calc_offset" in data:
            self.lbl_offset_value.setText(f"{data['calc_offset']:.2e}")
            
        # Clear mini plot or show something simple
        self.mini_ax.clear()
        plot_emittance_by_cutoff(self.mini_ax, emittance_file, rms_emittance,
                                 self.sigma_alpha_spin.value())
        self.mini_ax.set_title("Background subtraction", color=COLOR_TEXT, fontsize=10)
        # self.mini_ax.text(0.5, 0.5, "Ready for Science", ha='center', va='center', 
        #                  color=COLOR_GRID, transform=self.mini_ax.transAxes)
        self.mini_canvas.draw()

    def get_fitting_params(self):
        return {
            "sigma_clip": self.sigma_clip_enable.isChecked(),
            "sigma_alpha": self.sigma_alpha_spin.value(),
            "offset": self.offset_enable.isChecked(),
        }

