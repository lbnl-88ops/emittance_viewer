from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction

class AppMenu:
    def __init__(self, owner):
        self._owner = owner

    def populate_menu(self, menu_bar: QMenuBar):
        hamburger_menu = menu_bar.addMenu("☰")
        
        open_data_action = QAction("Open data directory", self._owner)
        open_data_action.triggered.connect(self._owner.open_data_directory)
        hamburger_menu.addAction(open_data_action)
        
        open_config_action = QAction("Open configuration directory", self._owner)
        open_config_action.triggered.connect(self._owner.open_config_directory)
        hamburger_menu.addAction(open_config_action)
        
        hamburger_menu.addSeparator()
        
        diagnostic_action = QAction("Open diagnostic window", self._owner)
        diagnostic_action.triggered.connect(self._owner.diagnostic_mode)
        hamburger_menu.addAction(diagnostic_action)
        
        hamburger_menu.addSeparator()
        
        quit_action = QAction("Quit", self._owner)
        quit_action.triggered.connect(self._owner.quit)
        hamburger_menu.addAction(quit_action)
