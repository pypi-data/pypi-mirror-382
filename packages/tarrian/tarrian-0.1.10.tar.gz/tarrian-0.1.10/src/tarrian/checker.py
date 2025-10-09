"""
checker.py - Modul pemeriksa lingkungan Tarrian
Memastikan dependensi (Python, Lark, Tarri) sudah tersedia.
"""

import shutil
import importlib
from tarrian.utils import run_cmd
from tarrian import __version__  # Ambil versi langsung dari __init__.py



def check_python():
    """Periksa apakah Python terpasang."""
    return shutil.which("python3") is not None or shutil.which("python") is not None


def check_pip():
    """Periksa apakah pip tersedia."""
    return shutil.which("pip") is not None or shutil.which("pip3") is not None


def check_lark():
    """Periksa apakah Lark sudah terpasang."""
    try:
        import lark
        return True
    except ImportError:
        return False


def check_tarri():
    """Periksa apakah Tarri sudah terpasang."""
    try:
        import tarri
        return True
    except ImportError:
        return False


def get_module_version(module_name):
    """Coba ambil versi langsung dari modul Python."""
    try:
        mod = importlib.import_module(module_name)
        return getattr(mod, "__version__", "-")
    except Exception:
        return "-"


def get_version(cmd):
    """Ambil versi dari perintah CLI (fallback jika gagal)."""
    output = run_cmd(cmd)
    if output:
        text = output.strip().replace("Python ", "").replace("pip ", "")
        return text.split()[0] if text else "-"
    return "-"


def show_summary():
    """Tampilkan ringkasan status lingkungan Tarrian secara sederhana."""
    print(f"Inisialisasi Komponen Tarrian | {__version__}")
    print("")

    python_ok = check_python()
    pip_ok = check_pip()
    lark_ok = check_lark()
    tarri_ok = check_tarri()

    python_ver = get_version("python3 --version") if python_ok else "-"
    pip_ver = get_version("pip --version") if pip_ok else "-"
    lark_ver = get_module_version("lark") if lark_ok else "-"
    tarri_ver = get_module_version("tarri") if tarri_ok else "-"

    print(f"[{'✓' if python_ok else '✗'}] Python {'ditemukan' if python_ok else 'tidak ditemukan'} ({python_ver})")
    print(f"[{'✓' if pip_ok else '✗'}] Pip {'ditemukan' if pip_ok else 'tidak ditemukan'} ({pip_ver})")
    print(f"[{'✓' if lark_ok else '✗'}] Lark {'ditemukan' if lark_ok else 'tidak ditemukan'}" +
          (f" ({lark_ver})" if lark_ok else ""))
    print(f"[{'✓' if tarri_ok else '✗'}] Tarri {'terinstal' if tarri_ok else 'belum terinstal'}" +
          (f" ({tarri_ver})" if tarri_ok else ""))

    print()
    if not all([python_ok, pip_ok, lark_ok, tarri_ok]):
        print("Beberapa komponen belum tersedia.")
        print("Gunakan `tarrian pasang tarri` untuk menyiapkan semua komponen dan menginstall Tarri.")
    else:
        print("Semua komponen telah terpasang dengan baik.")
