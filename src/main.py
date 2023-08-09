import sys
from PyQt5.QtWidgets import QApplication

from src.controllers.application import ApplicationController
from src.views.application import ApplicationView


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    exit()


def main():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    mainView = ApplicationView()
    mainController = ApplicationController(mainView)
    mainController.show()

    app.exec()


if __name__ == "__main__":
    main()
