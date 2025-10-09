"""
cli.py - Command Line Interface untuk Tarrian
Tarrian: Pengelola instalasi Bahasa Tarri (mirip Composer)
"""

import sys
from tarrian import checker, installer, __version__

def tampilkan_bantuan():
    print("Penggunaan: tarrian [perintah]")
    print("Perintah yang tersedia:")
    print("  cek                 → Periksa lingkungan sistem")
    print("  pasang tarri        → Instal Bahasa Tarri")
    print("  perbarui tarri      → Perbarui Bahasa Tarri")
    print("  hapus tarri         → Hapus Bahasa Tarri")
    print("  -v, --versi         → Tampilkan versi Tarrian")

def main():
    if len(sys.argv) < 2:
        tampilkan_bantuan()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    # Tambahan untuk versi
    if cmd in ("-v", "--versi"):
        print(f"Tarrian | v{__version__}")
        sys.exit(0)

    if cmd == "cek":
        checker.show_summary()

    elif cmd == "pasang":
        if len(sys.argv) > 2 and sys.argv[2].lower() == "tarri":
            installer.install_tarri()
        else:
            print("Gunakan: tarrian pasang tarri")

    elif cmd == "perbarui":
        if len(sys.argv) > 2 and sys.argv[2].lower() == "tarri":
            installer.update_tarri()
        else:
            print("Gunakan: tarrian perbarui tarri")

    elif cmd == "hapus":
        if len(sys.argv) > 2 and sys.argv[2].lower() == "tarri":
            installer.remove_tarri()
        else:
            print("Gunakan: tarrian hapus tarri")

    else:
        print(f"Perintah '{cmd}' tidak dikenal.")
        print("Gunakan 'tarrian' tanpa argumen untuk bantuan.")

if __name__ == "__main__":
    main()
