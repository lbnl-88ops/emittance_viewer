import logging
import datetime as dt
import os
from pathlib import Path
from typing import List

import numpy as np
from matplotlib.artist import Artist

from ops.ecris.analysis.model.emittance_scan import EmittanceScan
from ops.ecris.analysis.io.read_emittance_scan_file import (
    _file_raw_timestamp,
    load_emittance_scan,
    _file_formatted_timestamp,
)


class EmittanceScanFile:
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.filename = self.path.name
        self.plotted: bool = False
        self.file_size: float = file_size
        self.valid: bool = file_size > 0
        self.timestamp = _file_formatted_timestamp(path)
        self.raw_timestamp = _file_raw_timestamp(path)
        self._emittance_scan = None
        self._artist = None

    def __eq__(self, value: object) -> bool:
        if isinstance(value, EmittanceScanFile):
            return value.filename == self.filename
        return False

    @property
    def artist(self) -> Artist | None:
        return self._artist

    @artist.setter
    def artist(self, to_set):
        self._artist = to_set

    def clear_artist(self):
        if self._artist is not None:
            self._artist.remove()
            self._artist = None

    @property
    def formatted_datetime(self) -> str:
        if self.timestamp is not None:
            return self.timestamp
        else:
            return "Invalid timestamp"

    def unload_emittance_scan(self) -> None:
        self._emittance_scan = None

    @property
    def emittance_scan(self) -> EmittanceScan | None:
        if not self.valid:
            return None
        try:
            if self._emittance_scan is None:
                logging.info(f"Loading emittance scan data for file {self.filename}")
                self.valid = True
                self._emittance_scan = load_emittance_scan(self.path)
            return self._emittance_scan
        except BaseException as e:
            logging.info(f"File is invalid: {self.path}: {e}")
            self.valid = False
            return None

    @property
    def list_value(self) -> str:
        return f"{self.raw_timestamp:.0f} ({self.formatted_datetime})"
