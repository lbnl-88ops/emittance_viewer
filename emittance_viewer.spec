# PyInstaller spec for Emittance Viewer.
#
# Why a .spec file instead of a single `pyinstaller ...` CLI command:
# This app pulls in implicit *namespace packages* (ops.ecris and
# ops.ecris.analysis are two separate distributions that both contribute
# to the `ops` / `ops.ecris` namespace) plus a Qt-based matplotlib backend.
# PyInstaller's static import scanner frequently fails to discover:
#   - modules only reachable through a namespace package
#   - matplotlib's chosen backend (backend_qtagg) and its Qt bindings
#   - our own `emittance_viewer` subpackages if any module is only
#     imported indirectly
# `--collect-all` / `collect_submodules` calls below make all of that
# explicit instead of relying on PyInstaller's guesswork, which is the
# most likely reason the previous --onedir build opened and silently
# closed: an ImportError at startup with no console to show it on.
#
# Usage:
#   Release (no console window):
#     pyinstaller emittance_viewer.spec
#   Debug (keeps a console window open so you can see tracebacks):
#     EMITTANCE_VIEWER_DEBUG=1 pyinstaller emittance_viewer.spec
#
# The GitHub Actions workflow builds the release variant by default and
# has a manually-triggerable debug job (see .github/workflows/main.yml).

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

DEBUG_BUILD = os.environ.get("EMITTANCE_VIEWER_DEBUG") == "1"

datas = []
binaries = []
hiddenimports = []

# --- Our own package -------------------------------------------------
# app.py only imports `emittance_viewer.app`, so PyInstaller's static
# analysis starts there. Anything in the package tree not reached by a
# top-level `import` statement (e.g. modules only imported lazily, like
# `import matplotlib.pyplot as plt` inside a method) can be missed.
# collect_submodules walks the whole package explicitly so nothing is
# left out.
hiddenimports += collect_submodules("emittance_viewer")

# --- Namespace packages: ops.ecris / ops.ecris.analysis ---------------
# These ship as PEP 420 implicit namespace packages (no top-level
# `ops/__init__.py`), split across two separate pip distributions
# (ops.ecris and ops.ecris.analysis). PyInstaller's default hook does not
# reliably walk namespace packages, so we collect them explicitly.
for pkg in ("ops", "ops.ecris", "ops.ecris.analysis"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

# --- matplotlib Qt backend --------------------------------------------
# patchMatplotlib.py calls matplotlib.use("QtAgg") and plot.py imports
# matplotlib.backends.backend_qtagg directly, but PyInstaller does not
# always resolve the backend module from the use() call, and the PyQt6
# submodules matplotlib depends on (QtWidgets, QtGui, QtCore, sip) are
# easy to miss.
hiddenimports += [
    "matplotlib.backends.backend_qtagg",
    "matplotlib.backends.backend_qt5agg",
    "PyQt6.QtWidgets",
    "PyQt6.QtGui",
    "PyQt6.QtCore",
    "PyQt6.sip",
]

# --- h5py --------------------------------------------------------------
# h5py loads its HDF5 C extension dynamically; collect_all pulls in the
# compiled libs and any hidden submodules PyInstaller's scanner misses.
pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all("h5py")
datas += pkg_datas
binaries += pkg_binaries
hiddenimports += pkg_hiddenimports

# --- appdirs -------------------------------------------------------------
# Used for both the config directory (files/configuration.py) and the
# temp/cache directory (files/client.py). Small, but make sure it's
# included explicitly since it's imported indirectly relative to app.py's
# entry point analysis.
hiddenimports += ["appdirs"]


a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="emittance_viewer",
    debug=DEBUG_BUILD,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # console=True (Debug build): a console window stays open and shows
    # print()/traceback output, including anything our excepthook in
    # emittance_viewer/logging_setup.py logs.
    # console=False (Release build): the --noconsole behavior the
    # release is shipped with.
    console=DEBUG_BUILD,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="emittance_viewer",
)
