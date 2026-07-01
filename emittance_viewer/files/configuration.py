from dataclasses import dataclass, field, asdict
from logging import info
from pathlib import Path
from tomllib import load
from PyQt6.QtWidgets import QMessageBox
import tomllib
from typing import List, Optional

from appdirs import user_config_dir

from ops.ecris.analysis.model import Element

APP_NAME = "emittance_viewer"
APP_AUTHOR = "lbnl_88ops"
CONFIG_FILENAME = "config.toml"
CONFIG_FILEPATH = Path(user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_FULLPATH = CONFIG_FILEPATH / CONFIG_FILENAME

DATA_DIRECTORY = "default_data_directory"


@dataclass
class AppConfiguration:
    default_directory: Path = Path(".")
    custom_elements: List[Element] = field(default_factory=list)
    window_width: int = 1200
    window_height: int = 800
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    sash_position: Optional[int] = None


def load_configuration() -> AppConfiguration | None:
    if not CONFIG_FULLPATH.exists():
        return None
    else:
        try:
            with open(CONFIG_FULLPATH, "rb") as f:
                config = load(f)
                custom_elements = []
                if "element" in config:
                    info("Custom elements found")
                    for name, data in config["element"].items():
                        info(f"Parsing custom element: {name}")
                        try:
                            custom_elements.append(
                                Element(
                                    name=name,
                                    symbol=data["symbol"],
                                    atomic_mass=data["atomic_mass"],
                                    atomic_number=data["atomic_number"],
                                )
                            )
                            info(f"Parsed element {custom_elements[-1]}")
                        except KeyError as e:
                            info(f"Error parsing custom element: {e}")
                            continue

                return AppConfiguration(
                    default_directory=Path(config.get(DATA_DIRECTORY, ".")).absolute(),
                    custom_elements=custom_elements,
                    window_width=config.get("window_width", 1200),
                    window_height=config.get("window_height", 800),
                    window_x=config.get("window_x"),
                    window_y=config.get("window_y"),
                    sash_position=config.get("sash_position"),
                )
        except tomllib.TOMLDecodeError:
            QMessageBox.critical(
                None, "Error", "Error loading configuration, using default settings"
            )
            return AppConfiguration()


def save_configuration(config: AppConfiguration):
    """Save the configuration to the TOML file."""
    CONFIG_FILEPATH.mkdir(exist_ok=True, parents=True)

    lines = []
    lines.append(f'{DATA_DIRECTORY} = "{config.default_directory}"')
    lines.append(f"window_width = {config.window_width}")
    lines.append(f"window_height = {config.window_height}")
    if config.window_x is not None:
        lines.append(f"window_x = {config.window_x}")
    if config.window_y is not None:
        lines.append(f"window_y = {config.window_y}")
    if config.sash_position is not None:
        lines.append(f"sash_position = {config.sash_position}")

    lines.append("")

    if config.custom_elements:
        for el in config.custom_elements:
            lines.append(f'[element."{el.name}"]')
            lines.append(f'symbol = "{el.symbol}"')
            lines.append(f"atomic_mass = {el.atomic_mass}")
            lines.append(f"atomic_number = {el.atomic_number}")
            lines.append("")

    with open(CONFIG_FULLPATH, "w") as f:
        f.write("\n".join(lines))


def create_configuration() -> AppConfiguration:
    CONFIG_FILEPATH.mkdir(exist_ok=True, parents=True)
    config = AppConfiguration()
    save_configuration(config)
    return config
