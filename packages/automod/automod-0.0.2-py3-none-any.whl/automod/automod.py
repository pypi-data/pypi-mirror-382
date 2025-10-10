import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow


def main():
    app = QApplication()
    app.setApplicationDisplayName("AutoMod")
    app.setDesktopFileName("AutoMod")
    app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    app.setQuitOnLastWindowClosed(True)
    app.setWindowIcon(QIcon("icons/app_icon.png"))

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
