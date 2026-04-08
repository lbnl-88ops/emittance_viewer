from emittance_viewer import EmittanceViewer
from emittance_viewer.files.configuration import load_configuration, AppConfiguration


def emittance_viewer():
    app = EmittanceViewer(load_configuration())
    app.mainloop()


# Create the main window
if __name__ == "__main__":
    emittance_viewer()
