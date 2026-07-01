from pathlib import Path
from typing import List
from logging import info
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt

from ops.ecris.drivers.venus_plc import VENUS_PLC_DATA_DEFINITIONS, GAS_NAMES
from emittance_viewer.files import EmittanceScanFile
from emittance_viewer.gui.style.constants import COLOR_BG, FONT_SANS
from emittance_viewer.gui.style.styles import LIST_STYLE

class FileComparisonWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSD File Comparison")
        self.resize(800, 600)
        self.setStyleSheet(f"background: {COLOR_BG}; font-family: {FONT_SANS};")
        self.layout = QVBoxLayout(self)
        
        self.files: List[EmittanceScanFile] = []
        
        self.tree_view = QTreeWidget()
        self.tree_view.setStyleSheet(LIST_STYLE)
        self.layout.addWidget(self.tree_view)
        
        self.show()

    def add_files(self, paths: List[Path]) -> None:
        info(f"Adding files {paths} to comparison window")
        self.files.extend([EmittanceScanFile(p, 1) for p in paths])
        self._render_data()

    def add_file(self, path: Path) -> None:
        info(f"Adding file {path} to comparison window")
        self.files.append(EmittanceScanFile(path, 1))
        self._render_data()

    def _render_data(self) -> None:
        self.tree_view.clear()
        
        labels_by_category = VENUS_PLC_DATA_DEFINITIONS.labels_by_category
        self.files = sorted(
            self.files,
            key=lambda file: file.raw_timestamp
            if file.raw_timestamp is not None
            else 0,
            reverse=True,
        )
        
        headers = ["Parameter"] + [file.formatted_datetime for file in self.files]
        self.tree_view.setColumnCount(len(headers))
        self.tree_view.setHeaderLabels(headers)
        
        scans = [file.emittance_scan for file in self.files]
        
        for category, labels in labels_by_category.items():
            category_item = QTreeWidgetItem(self.tree_view, [category])
            
            for label in labels:
                def get_value(settings_dict):
                    if label.key not in settings_dict:
                        return ""
                    value = settings_dict[label.key]
                    if label.units == "boolean":
                        value = str(bool(value))
                    if label.key.startswith("gas_name"):
                        value = GAS_NAMES[int(value)]
                    return str(value)

                units = f"({label.units})" if label.units != "nan" else ""
                values = [
                    get_value(csd.extra_metadata) if csd is not None else "" 
                    for csd in scans
                ]
                
                QTreeWidgetItem(category_item, [f"{label.label} {units}"] + values)
            
            category_item.setExpanded(True)

    def on_close(self):
        self.close()
