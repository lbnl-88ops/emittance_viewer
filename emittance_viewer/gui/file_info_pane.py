from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
import numpy as np

from emittance_viewer.files.emittance_file import EmittanceScanFile
from emittance_viewer.gui.style.constants import COLOR_ACTION, COLOR_BG, COLOR_GRID, COLOR_PLOT_BG, FONT_MONO, FONT_SANS
from emittance_viewer.gui.style.styles import TITLE_LABEL_STYLE

class FileInfoPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("Scan information")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(TITLE_LABEL_STYLE)
        self.layout.addWidget(self.title_label)
        
        self.info_table_container = QWidget()
        self.info_table = QGridLayout(self.info_table_container)
        self.info_table.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.info_table_container)
        
        self.file_frames = []

    def clear_info(self):
        while self.info_table.count():
            item = self.info_table.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.file_frames = []

    def add_file_info(self, files: List[EmittanceScanFile]):
        self.clear_info()
        n_files = len(files)
        if n_files == 0:
            return

        n_cols = 2 if n_files > 1 else 1

        for i, file in enumerate(files):
            row = i // n_cols
            col = i % n_cols

            # Determine if utilization is low
            is_low_utilization = False
            mult = None
            max_current = None
            utilization = None
            try:
                mult = file.emittance_scan.extra_metadata["emittance_keithley_multiplier"]
                max_current = np.max(file.emittance_scan.data)
                utilization = 100 * (max_current * 10**mult) / 10
                # Use rounded value for threshold check to avoid UI discrepancy
                if round(utilization) < 10:
                    is_low_utilization = True
            except (KeyError, AttributeError, TypeError):
                pass

            # Container for each file's info (the "square")
            outer_frame = QFrame()
            # NOTE: QLabel is itself a QFrame subclass, so a bare "QFrame { ... }"
            # selector here matches every label inside this frame too, giving
            # each piece of text its own thin border. Scope the rule to this
            # specific widget with an object name so only the outer square
            # gets the border/background; children are left untouched.
            outer_frame.setObjectName("fileInfoOuterFrame")
            outer_frame.setStyleSheet(
                f"QFrame#fileInfoOuterFrame {{ border: 1px solid {COLOR_GRID}; background: {COLOR_BG}; }}"
            )
                
            outer_layout = QVBoxLayout(outer_frame)
            
            # Title: Timestamp
            title_label = QLabel(file.formatted_datetime)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"font-family: {FONT_SANS}; font-weight: bold;")
            outer_layout.addWidget(title_label)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(5, 5, 5, 5)
            outer_layout.addWidget(content_widget)

            if mult is not None:
                # Use FONT_MONO for data
                val_style = f"font-family: {FONT_MONO};"
                if is_low_utilization:
                    # Highlight just the data part in orange
                    val_style_highlighted = val_style + f" color: {COLOR_ACTION}; font-weight: bold;"
                else:
                    val_style_highlighted = val_style
                
                # Gain
                gain_layout = QHBoxLayout()
                lbl_gain = QLabel("Gain:")
                lbl_gain.setStyleSheet(f"font-family: {FONT_SANS};")
                gain_layout.addWidget(lbl_gain)
                gain_val = QLabel(f"10^{mult}")
                gain_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                gain_val.setStyleSheet(val_style)
                gain_layout.addWidget(gain_val)
                content_layout.addLayout(gain_layout)

                # Max Current
                current_layout = QHBoxLayout()
                lbl_max_i = QLabel("Max I:")
                lbl_max_i.setStyleSheet(f"font-family: {FONT_SANS};")
                current_layout.addWidget(lbl_max_i)
                current_val = QLabel(f"{max_current:.2e} A")
                current_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                current_val.setStyleSheet(val_style)
                current_layout.addWidget(current_val)
                content_layout.addLayout(current_layout)

                # Utilization
                util_layout = QHBoxLayout()
                lbl_util = QLabel("Util:")
                lbl_util.setStyleSheet(f"font-family: {FONT_SANS};")
                util_layout.addWidget(lbl_util)
                util_val = QLabel(f"{utilization:.0f}%")
                util_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                util_val.setStyleSheet(val_style_highlighted)
                util_layout.addWidget(util_val)
                content_layout.addLayout(util_layout)

                if is_low_utilization:
                    rec_text = f"Suggest: 10^{mult + 1} ({utilization * 10:.0f}%)"
                    rec_label = QLabel(rec_text)
                    rec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    rec_label.setStyleSheet(f"font-family: {FONT_SANS}; font-weight: bold; color: {COLOR_ACTION};")
                    outer_layout.addWidget(rec_label)
            else:
                no_data_label = QLabel("No data")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content_layout.addWidget(no_data_label)

            self.info_table.addWidget(outer_frame, row, col)
            self.file_frames.append(outer_frame)
