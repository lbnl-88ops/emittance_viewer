from logging import Handler, getLogger, info
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt

class DiagnosticWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Diagnostics Log')
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
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
