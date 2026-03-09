import tkinter as tk


class AppMenu(tk.Menu):
    def __init__(
        self,
        owner,
        *args,
        **kwargs,
    ):
        super().__init__(owner, relief=tk.FLAT, *args, **kwargs)
        self._owner = owner
        self.create_menus()

    def create_menus(self):
        self.hamburger_menu = tk.Menu(self, tearoff=0, borderwidth=3, border=1)
        self.add_cascade(label="☰", menu=self.hamburger_menu)
        self.hamburger_menu.add_command(
            label="Open data directory", command=self._owner.open_data_directory
        )
        self.hamburger_menu.add_command(
            label="Open configuration directory",
            command=self._owner.open_config_directory,
        )
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_command(
            label="Open diagnostic window", command=self._owner.diagnostic_mode
        )
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_command(label="Quit", command=self._owner.quit)
