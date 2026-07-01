from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
import numpy as np

from emittance_viewer.files.emittance_file import EmittanceScanFile

class FileInfoPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("Scan information")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
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
            outer_frame.setFrameShape(QFrame.Shape.StyledPanel)
            outer_frame.setLineWidth(1)
            
            if is_low_utilization:
                outer_frame.setStyleSheet("""
                    QFrame {
                        background-color: #ffcccc; 
                        border: none;
                    }
                    QLabel {
                        color: black;
                    }
                """)
            else:
                outer_frame.setStyleSheet("QFrame { border: none; }")
                
            outer_layout = QVBoxLayout(outer_frame)
            
            # Title: Timestamp
            title_label = QLabel(file.formatted_datetime)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_font = title_label.font()
            title_font.setBold(True)
            title_label.setFont(title_font)
            outer_layout.addWidget(title_label)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(5, 5, 5, 5)
            outer_layout.addWidget(content_widget)

            if mult is not None:
                # Gain
                gain_layout = QHBoxLayout()
                gain_layout.addWidget(QLabel("Gain:"))
                gain_val = QLabel(f"10^{mult}")
                gain_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                gain_layout.addWidget(gain_val)
                content_layout.addLayout(gain_layout)

                # Max Current
                current_layout = QHBoxLayout()
                current_layout.addWidget(QLabel("Max I:"))
                current_val = QLabel(f"{max_current:.2e} A")
                current_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                current_layout.addWidget(current_val)
                content_layout.addLayout(current_layout)

                # Utilization
                util_layout = QHBoxLayout()
                util_layout.addWidget(QLabel("Util:"))
                util_val = QLabel(f"{utilization:.0f}%")
                util_val.setAlignment(Qt.AlignmentFlag.AlignRight)
                util_layout.addWidget(util_val)
                content_layout.addLayout(util_layout)

                if is_low_utilization:
                    rec_text = f"Suggest: 10^{mult + 1} ({utilization * 10:.0f}%)"
                    rec_label = QLabel(rec_text)
                    rec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    rec_label.setStyleSheet("font-style: italic; color: darkred;")
                    outer_layout.addWidget(rec_label)
            else:
                no_data_label = QLabel("No data")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content_layout.addWidget(no_data_label)

            self.info_table.addWidget(outer_frame, row, col)
            self.file_frames.append(outer_frame)
