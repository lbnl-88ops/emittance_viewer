from logging import getLogger
from pathlib import Path
from typing import List

import requests

_log = getLogger(__name__)

API_URL = "http://ecris.lbl.gov:5000"
TEMP_FOLDER = Path("./tmp/")


def list_local_files(directory: Path) -> List[Path]:
    return [f.resolve() for f in directory.glob("csd_*")]


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


def download_filepair(filepath: Path):
    csd_filename = str(filepath.name)
    dsht_filename = csd_filename.replace("csd", "dsht")
    download_file(dsht_filename)
    return download_file(csd_filename)


def download_file(filename: str) -> Path | None:
    """Download a file from the API and save it as a temporary file."""
    _log.info(f"Attempting to download {filename}")
    TEMP_FOLDER.mkdir(exist_ok=True)
    response = requests.get(f"{API_URL}/download/{filename}")
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
