"""
Tarrian - Pengelola instalasi dan pembaruan Bahasa Tarri.
Dibuat oleh Ketut Dana | TARRI Dev
"""

__version__ = "0.1.10"
__author__ = "Ketut Dana"
__license__ = "MIT"

from .cli import main

# Ketika package dijalankan langsung: python -m tarrian
if __name__ == "__main__":
    main()
