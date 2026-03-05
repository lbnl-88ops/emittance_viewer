from logging import getLogger
from pathlib import Path
from typing import List

import requests

_log = getLogger(__name__)

API_URL = "http://ecris.lbl.gov:5000"
TEMP_FOLDER = Path("./tmp/")


def list_local_files(directory: Path) -> List[Path]:
    return [f.resolve() for f in directory.glob("emittance_scan_*.h5")]


def list_files() -> List[Path]:
    url = f"{API_URL}/files"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return [Path(filename) for filename in response.json()]
        else:
            _log.error(f"Failed to retrieve files from {url}")
            return []
    except requests.Timeout:
        _log.error(f"Timeout occurred while trying to connect to {url}")
    except requests.RequestException as e:
        _log.error(f"An error occurred while trying to connect to {url}: {e}")
    return []


def download_file(filename: Path) -> Path | None:
    """Download a file from the API and save it as a temporary file."""
    _log.info(f"Attempting to download {filename}")
    TEMP_FOLDER.mkdir(exist_ok=True)
    response = requests.get(f"{API_URL}/download/{filename.name}")
    if response.status_code == 200:
        temp_file = TEMP_FOLDER / filename
        with open(temp_file, "wb") as f:
            f.write(response.content)
        return temp_file
    else:
        print("File not found on server.")
        return None


def clear_temp_files() -> None:
    if TEMP_FOLDER.exists():
        for file in TEMP_FOLDER.glob("*"):
            file.unlink()
