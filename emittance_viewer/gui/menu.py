import tkinter as tk


class AppMenu(tk.Menu):
    def __init__(
        self,
        owner,
        use_blitting: tk.BooleanVar,
        rescale: tk.BooleanVar,
        *args,
        **kwargs,
    ):
        super().__init__(owner, relief=tk.FLAT, *args, **kwargs)
        self._owner = owner
        self.create_menus(use_blitting, rescale)

    def create_menus(self, use_blitting, rescale):
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
        self.hamburger_menu.add_checkbutton(
            label="Rescale",
            variable=rescale,
            command=self._owner.toggle_rescale,
            onvalue=True,
            offvalue=False,
        )
        self.hamburger_menu.add_checkbutton(
            label="Use blitting",
            variable=use_blitting,
            command=self._owner.toggle_blitting,
            onvalue=True,
            offvalue=False,
        )
        self.hamburger_menu.add_command(
            label="Open diagnostic window", command=self._owner.diagnostic_mode
        )
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_command(
            label="Export data...", command=self._owner.export_data
        )
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_command(label="Quit", command=self._owner.quit)
