#!/usr/bin/env python3
"""
Main entry point for the Family Photo Organizer application.
"""

import sys
from PySide6.QtWidgets import QApplication
from family_photo_organizer import __version__
from family_photo_organizer.gui.main_window import MainWindow


def main():
    """
    Main function to start the application.
    """
    print(f"Starting Family Photo Organizer v{__version__}")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())