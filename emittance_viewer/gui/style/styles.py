from PyQt6.QtWidgets import QLayout, QPushButton, QLabel
from emittance_viewer.gui.style.constants import (
    FONT_SANS, FONT_MONO, COLOR_TEXT, COLOR_GRID, COLOR_PLOT_BG, COLOR_BG, COLOR_ACTION
)

MENU_STYLE = f"""
    QMenuBar {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; font-family: {FONT_SANS}; }}
    QMenuBar::item:selected {{ background-color: {COLOR_GRID}; }}
    QMenu {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; border: 1px solid {COLOR_GRID}; font-family: {FONT_SANS}; }}
    QMenu::item {{ padding: 5px 25px 5px 20px; }}
    QMenu::item:selected {{ background-color: {COLOR_GRID}; color: {COLOR_TEXT}; }}
    QMenu::separator {{ height: 1px; background: {COLOR_GRID}; margin: 5px 0px 5px 0px; }}
"""

GROUP_BOX_STYLE = f"""
    QGroupBox {{ font-family: {FONT_SANS}; color: {COLOR_TEXT}; font-weight: bold;
                 border: 1px solid {COLOR_GRID}; margin-top: 1.2ex; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 0px; }}
"""

LABEL_STYLE = f"font-family: {FONT_SANS}; font-size: 11px; color: {COLOR_TEXT};"
TITLE_LABEL_STYLE = f"font-family: {FONT_SANS}; font-weight: bold; font-size: 14px; color: {COLOR_TEXT};"
LIST_STYLE = f"background: {COLOR_PLOT_BG}; font-family: {FONT_MONO}; color: {COLOR_TEXT}; border: 1px solid {COLOR_GRID};"
BUTTON_STYLE = f"font-family: {FONT_SANS}; padding: 5px 12px;"
ACTION_BUTTON_STYLE = f"background: {COLOR_ACTION}; color: white; font-weight: bold; font-family: {FONT_SANS}; padding: 6px 12px;"

MODE_INDICATOR_STYLE = f"""
    padding: 4px; font-weight: bold; border-radius: 4px;
    font-family: {FONT_SANS}; color: white;
"""

def add_button(layout: QLayout, text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(BUTTON_STYLE)
    layout.addWidget(btn)
    return btn

def add_label(layout: QLayout, text: str, style: str = LABEL_STYLE) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(style)
    layout.addWidget(lbl)
    return lbl
