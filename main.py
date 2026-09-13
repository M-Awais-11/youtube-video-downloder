"""
Main application launcher for YouTube Video Downloader.
"""
import sys
import os
import tkinter as tk
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.main_window import MainWindow


def enable_high_dpi_awareness():
    """Enables High-DPI scaling on Windows for crisp typography and UI elements."""
    if sys.platform == "win32":
        try:
            import ctypes
            # Per-monitor DPI aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main():
    enable_high_dpi_awareness()

    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
