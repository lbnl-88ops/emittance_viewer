from logging import getLogger
from pathlib import Path
from typing import List

import requests
from appdirs import user_cache_dir

_log = getLogger(__name__)

API_URL = "http://ecris.lbl.gov:5000"

# NOTE: This used to be a relative "./tmp/" folder. That is fragile once the
# app is installed under Program Files (no write access without admin
# rights) or run from any directory other than the source checkout. Use the
# OS-appropriate per-user cache directory instead, which is always writable
# by the user running the app (e.g. on Windows:
# C:\Users\<user>\AppData\Local\lbnl_88ops\emittance_viewer\Cache).
TEMP_FOLDER = Path(user_cache_dir("emittance_viewer", "lbnl_88ops")) / "tmp"


def list_local_files(directory: Path) -> List[Path]:
    return [f.resolve() for f in directory.glob("emittance_scan_*.h5")]


def list_files() -> List[Path]:
    url = f"{API_URL}/emittance_files"
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
    TEMP_FOLDER.mkdir(exist_ok=True, parents=True)
    response = requests.get(f"{API_URL}/download/{filename.name}")
    if response.status_code == 200:
        temp_file = TEMP_FOLDER / filename.name
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
