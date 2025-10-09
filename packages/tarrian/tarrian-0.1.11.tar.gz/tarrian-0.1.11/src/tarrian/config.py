"""
config.py - Konfigurasi utama untuk Tarrian
Berisi informasi versi, URL instalasi, dan path penting.
"""

import os
from pathlib import Path
from tarrian import __version__  # Ambil versi langsung dari __init__.py

# Versi Tarrian (sinkron otomatis dengan __init__.py)
TARRIAN_VERSION = __version__

# Versi minimum Python yang direkomendasikan
MIN_PYTHON_VERSION = (3, 9)

# Nama paket Tarri di PyPI
TARRI_PACKAGE_NAME = "tarri"

# URL PyPI untuk instalasi Tarri
# (Gunakan test.pypi.org untuk development)
TARRI_PYPI_URL = "https://test.pypi.org/simple/"

# URL fallback untuk PyPI utama (jika test gagal)
TARRI_PYPI_FALLBACK = "https://pypi.org/simple/"

# URL download Python installer (untuk Windows atau Linux)
PYTHON_DOWNLOAD_URL = {
    "windows": "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe",
    "linux": "https://www.python.org/downloads/source/",
    "mac": "https://www.python.org/downloads/macos/"
}

# Nama modul parser yang diperlukan
REQUIRED_MODULES = ["lark-parser"]

# Folder kerja pengguna
USER_HOME = Path.home()
TARRIAN_DIR = USER_HOME / ".tarrian"

# Buat folder tarrian jika belum ada
os.makedirs(TARRIAN_DIR, exist_ok=True)

# File log untuk menyimpan aktivitas instalasi
LOG_FILE = TARRIAN_DIR / "tarrian.log"
