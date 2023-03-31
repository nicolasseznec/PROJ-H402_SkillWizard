import sys
from PyQt5.QtWidgets import QApplication

from src.MainWindow import MainWindow


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    exit()


def main():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
