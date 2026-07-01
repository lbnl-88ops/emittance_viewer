from logging import Handler, getLogger, info
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
from emittance_viewer.gui.style.constants import COLOR_BG, FONT_SANS
from emittance_viewer.gui.style.styles import LIST_STYLE

class DiagnosticWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Diagnostics Log')
        self.resize(600, 400)
        self.setStyleSheet(f"background: {COLOR_BG}; font-family: {FONT_SANS};")
        self.layout = QVBoxLayout(self)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(LIST_STYLE)
        self.layout.addWidget(self.log_text)

        class LogHandler(Handler):
            def __init__(self, text_widget):
                super().__init__()
                self._text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self._text_widget.append(msg)
        
        self.handler = LogHandler(self.log_text)
        getLogger().addHandler(self.handler)
        info('Opened diagnostic log window')        
        
        self.show()

    def closeEvent(self, event):
        getLogger().removeHandler(self.handler)
        event.accept()
