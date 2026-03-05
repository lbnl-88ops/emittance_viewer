from logging import Handler, getLogger, info
import tkinter as tk

class DiagnosticWindow(tk.Toplevel):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, takefocus=False)
        self.title('Diagnostics Log')
        self.log_text = tk.Text(self)
        self.log_text.pack(expand=True, fill='both')

        class LogHandler(Handler):
            def __init__(self, text_widget):
                super().__init__()
                self._text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self._text_widget.insert(tk.END, msg + '\n')
                self._text_widget.see(tk.END)
        
        self.handler = LogHandler(self.log_text)
        getLogger().addHandler(self.handler)
        info('Opened diagnostic log window')        

        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def on_close(self):
        getLogger().removeHandler(self.handler)
        self.destroy()
