"""
installer.py - Modul untuk mengelola instalasi Bahasa Tarri
Sekarang otomatis mendeteksi & mengunduh Python, pip, dan Lark jika belum ada.
Support: macOS, Linux (Debian/Ubuntu), dan Windows.
"""

import os
import sys
import platform
import urllib.request
import subprocess
import shutil
from tarrian import utils, checker

PYTHON_URLS = {
    "Windows": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe",
    "Darwin": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-macos11.pkg",
    "Linux": "https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz"
}


def download_file(url, dest):
    """Unduh file dari URL ke lokasi tujuan."""
    print(f"⬇️  Mengunduh: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"✅ File diunduh ke {dest}")
    except Exception as e:
        print(f"[tarrian | error] Gagal mengunduh {url}: {e}")
        return False
    return True


def install_python():
    """Unduh dan pasang Python jika belum tersedia."""
    os_name = platform.system()
    url = PYTHON_URLS.get(os_name)

    if not url:
        print(f"[tarrian | error] Sistem {os_name} belum didukung.")
        return False

    dest = os.path.join(os.getcwd(), os.path.basename(url))
    if not download_file(url, dest):
        return False

    print("📦 Memasang Python...")

    try:
        if os_name == "Windows":
            subprocess.run([dest, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
        elif os_name == "Darwin":
            subprocess.run(["sudo", "installer", "-pkg", dest, "-target", "/"], check=True)
        elif os_name == "Linux":
            subprocess.run(["tar", "-xzf", dest], check=True)
            os.chdir("Python-3.10.11")
            subprocess.run(["./configure"], check=True)
            subprocess.run(["make", "-j4"], check=True)
            subprocess.run(["sudo", "make", "altinstall"], check=True)
        print("✅ Python berhasil dipasang.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[tarrian | error] Gagal memasang Python: kode keluar {e.returncode}")
    except Exception as e:
        print(f"[tarrian | error] Gagal memasang Python: {e}")
    return False


def ensure_pip():
    """Pastikan pip terinstal."""
    if checker.check_pip():
        return True

    print("⚙️  Menginstal pip...")
    try:
        url = "https://bootstrap.pypa.io/get-pip.py"
        dest = os.path.join(os.getcwd(), "get-pip.py")
        if not download_file(url, dest):
            return False

        subprocess.run([sys.executable, dest], check=True)
        print("✅ Pip berhasil diinstal.")
        return True
    except Exception as e:
        print(f"[tarrian | error] Gagal menginstal pip: {e}")
        return False


def ensure_lark():
    """Pastikan Lark terinstal."""
    if checker.check_lark():
        return True

    print("[tarrian] Lark belum terpasang. Menginstal...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "lark-parser>=0.12.0"], check=True)
        print("✅ Lark berhasil diinstal.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[tarrian | error] Gagal memasang Lark: kode keluar {e.returncode}")
    except Exception as e:
        print(f"[tarrian | error] Gagal memasang Lark: {e}")
    return False


def install_tarri():
    """Instal Tarri beserta dependensinya."""
    utils.print_header()
    print("Memulai proses instalasi Bahasa Tarri...\n")

    if not utils.check_internet():
        print("[tarrian | gagal] Tidak ada koneksi internet.")
        return

    # 1️⃣ Pastikan Python
    if not checker.check_python():
        print("[tarrian] Python belum terpasang.")
        if utils.confirm("Apakah ingin menginstal Python otomatis?"):
            if not install_python():
                return
        else:
            print("[tarrian] Instalasi dibatalkan.")
            return

    # 2️⃣ Pastikan pip
    if not ensure_pip():
        return

    # 3️⃣ Pastikan Lark
    if not ensure_lark():
        return

    # 4️⃣ Instal Tarri
    print("\n Menginstal Bahasa Tarri dari PyPI...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--index-url", "https://test.pypi.org/simple/",
            "--extra-index-url", "https://pypi.org/simple",
            "tarri"
        ], check=True)
        print("\n✅ Bahasa Tarri berhasil dipasang!")
        print("   Coba jalankan perintah: tarri -v")
    except subprocess.CalledProcessError as e:
        print(f"[tarrian | error] Gagal menginstal Tarri: {e}")


def update_tarri():
    """Perbarui Tarri ke versi terbaru."""
    utils.print_header()
    print("🔄 Memperbarui Bahasa Tarri...\n")

    if not utils.check_internet():
        print("[tarrian | error] Tidak ada koneksi internet.")
        return

    subprocess.run([
        sys.executable, "-m", "pip", "install", "--upgrade",
        "--index-url", "https://test.pypi.org/simple/",
        "--extra-index-url", "https://pypi.org/simple",
        "tarri"
    ], check=True)

    print("\n✅ Bahasa Tarri berhasil diperbarui ke versi terbaru.")


def remove_tarri():
    """Hapus Tarri dari sistem."""
    utils.print_header()
    print("🧹 Menghapus Bahasa Tarri...\n")

    if not checker.check_tarri():
        print("[tarrian] Tarri belum terinstal di sistem.")
        return

    if utils.confirm("Apakah Anda yakin ingin menghapus Tarri?"):
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "tarri"], check=True)
        print("\n✅ Bahasa Tarri telah dihapus sepenuhnya.")
    else:
        print("[tarrian] Penghapusan dibatalkan.")
