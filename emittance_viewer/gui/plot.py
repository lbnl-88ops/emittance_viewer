from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from ..plotting.plot_emittance_scan import create_figure, plot_file
from emittance_viewer.files import EmittanceScanFile

class Plot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = None
        self.create_widgets(n_plots=0)

    def create_widgets(self, n_plots: int):
        import matplotlib.pyplot as plt
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            plt.close(self._figure)
            self.canvas.deleteLater()
            
        self._figure, self._axs = create_figure(n_plots)
        
        # Hide extra axes if they are not used
        if n_plots > 0:
            for i in range(n_plots, len(self._axs)):
                self._axs[i].set_visible(False)
        
        self.canvas = Figure(self._figure)

        self.layout.addWidget(self.canvas)
        self.canvas.draw()

    def clear_plot(self):
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

    def plot(self, files: List[EmittanceScanFile]):
        self.clear_plot()
        self.create_widgets(len(files))
        for ax, file in zip(self._axs, files):
            plot_file(ax, file)

class Figure(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)
