import logging
import datetime as dt
import os
from pathlib import Path
from typing import List

import numpy as np
from matplotlib.artist import Artist

from ops.ecris.analysis.model import CSD
from ops.ecris.analysis.io.read_csd_file import (
    _file_raw_timestamp,
    read_csd_from_file_pair,
    _file_formatted_timestamp,
)


class CSDFile:
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.filename = self.path.name
        self.plotted: bool = False
        self.file_size: float = file_size
        self.valid: bool = file_size > 0
        self.timestamp = _file_formatted_timestamp(path)
        self.raw_timestamp = _file_raw_timestamp(path)
        self._csd = None
        self._artist = None

    def __eq__(self, value: object) -> bool:
        if isinstance(value, CSDFile):
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

    def unload_csd(self) -> None:
        self._csd = None

    @property
    def csd(self) -> CSD | None:
        if not self.valid:
            return None
        try:
            if self._csd is None:
                logging.info(f"Loading CSD data for file {self.filename}")
                self.valid = True
                self._csd = read_csd_from_file_pair(self.path)
            logging.info(
                f"CSD data accessed: m_over_q exists {self._csd.m_over_q is not None}"
            )
            return self._csd
        except BaseException as e:
            logging.info(f"File is invalid: {self.path}: {e}")
            self.valid = False
            return None

    @property
    def list_value(self) -> str:
        return f"{self.raw_timestamp:.0f} ({self.formatted_datetime})"


def get_files(path: Path) -> List[CSDFile]:
    glob = "csd_" + "[0-9]" * 10
    return [
        CSDFile(p, file_size=os.path.getsize(p))
        for p in reversed(sorted(Path(path).glob(glob)))
    ]


def export_to_file(file_stream, files: List[CSDFile]):
    data = None
    headers = []
    for file in files:
        csd = file.csd
        if csd is None:
            raise ValueError(f"No CSD for file {file.filename}")
        elif csd.m_over_q is None:
            raise ValueError(f"No m_over_q calculated for file {file.filename}")
        print(csd.m_over_q.shape, csd.data.shape)
        if data is None:
            data = np.concatenate((csd.m_over_q.reshape(-1, 1), csd.data), axis=1)
        else:
            data = np.concatenate((data, csd.m_over_q.reshape(-1, 1), csd.data), axis=1)
        headers.append(
            ",".join(
                [
                    f"{col_name}_{file.filename}"
                    for col_name in [
                        "m_over_q",
                        "time",
                        "dipole_current",
                        "dipole_field",
                        "beam_current",
                    ]
                ]
            )
        )
    if data is not None:
        np.savetxt(
            file_stream, data, delimiter=",", header=",".join(headers), comments=""
        )
