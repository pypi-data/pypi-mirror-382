"""
utils.py - Fungsi bantu untuk Tarrian CLI
"""

import os
import platform
import subprocess
import shutil

# Ambil versi langsung dari tarrian/__init__.py
try:
    from tarrian import __version__
except ImportError:
    __version__ = "unknown"


def run_command(cmd: list, silent: bool = False):
    """
    Jalankan perintah terminal dan tampilkan output-nya.
    """
    try:
        if silent:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        else:
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[tarrian | error] Gagal menjalankan perintah: {' '.join(cmd)}")
        print(f"Kode keluar: {e.returncode}")
        raise


def run_cmd(cmd: str) -> str:
    """
    Jalankan perintah shell dan kembalikan output (stdout atau stderr).
    Kompatibel dengan fungsi lama Tarrian.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error: {e}"


def which_python():
    """
    Mengembalikan path Python yang sedang digunakan.
    """
    return shutil.which("python3") or shutil.which("python")


def get_os_info():
    """
    Kembalikan informasi sistem operasi secara ringkas.
    """
    return {
        "os": platform.system(),
        "version": platform.version(),
        "release": platform.release(),
        "arch": platform.machine(),
    }


def print_header():
    """
    Tampilkan header cantik Tarrian di terminal.
    """
    print("=" * 60)
    print("Tarrian Installer - Manajer Instalasi Bahasa Tarri")
    print(f"Versi: {__version__}")
    print("Sumber: https://test.pypi.org/project/tarri/")
    print("=" * 60)


def check_internet():
    """
    Cek koneksi internet sederhana dengan ping ke pypi.org
    """
    try:
        # Gunakan ping cross-platform (Windows & Unix)
        ping_cmd = ["ping", "-n", "1", "pypi.org"] if platform.system() == "Windows" else ["ping", "-c", "1", "pypi.org"]
        subprocess.check_call(
            ping_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def confirm(prompt: str) -> bool:
    """
    Tanya ya/tidak ke user sebelum lanjut.
    """
    resp = input(f"{prompt} (ya/tidak): ").lower().strip()
    return resp in ("y", "ya", "yes")
