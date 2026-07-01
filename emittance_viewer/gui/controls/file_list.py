from pathlib import Path
from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView, QListWidgetItem
from PyQt6.QtCore import pyqtSignal

from ops.ecris.analysis.io.read_emittance_scan_file import _file_formatted_timestamp

from emittance_viewer.gui.style.styles import LIST_STYLE

class FileList(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.files: List[Path] = []
        self.file_listbox = QListWidget()
        self.file_listbox.setStyleSheet(LIST_STYLE)
        self.file_listbox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.file_listbox.itemSelectionChanged.connect(self.selectionChanged.emit)
        
        self.layout.addWidget(self.file_listbox)

    def get_selected_file(self) -> Path | None:
        selected_items = self.file_listbox.selectedIndexes()
        if selected_items:
            return self.files[selected_items[0].row()]
        return None

    def fill_list_box(self, file_list: List[Path]):
        # Save current selection
        current_row = self.file_listbox.currentRow()
        
        filtered_files = []
        filenames = []
        for f in file_list:
            fmt = _file_formatted_timestamp(f)
            if fmt != "UNKNOWN":
                filtered_files.append(f)
                filenames.append(fmt)
        
        self.files = filtered_files
        self.file_listbox.clear()
        
        if not filenames:
            self.file_listbox.addItem("No files found")
            self.file_listbox.setEnabled(False)
        else:
            self.file_listbox.addItems(filenames)
            self.file_listbox.setEnabled(True)
            
            # Restore selection if possible
            if current_row >= 0 and current_row < self.file_listbox.count():
                self.file_listbox.setCurrentRow(current_row)
