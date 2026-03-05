import tkinter as tk


class StatusBarSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatusBarSingleton, cls).__new__(cls)
            cls._instance.status_var = tk.StringVar(value="Starting up...")
        return cls._instance

    def get_status_var(self) -> tk.StringVar:
        return self.status_var

    def update_status(self, info: str) -> None:
        self.status_var.set(info)


def update_status_bar(info: str) -> None:
    status_bar = StatusBarSingleton()
    status_bar.update_status(info)
