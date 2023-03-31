from importlib import resources

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox


class ResourceLoader:
    res_folder = "resources"
    ui_folder = res_folder + ".ui"
    ui_extension = ".ui"
    data_folder = res_folder + ".data"

    @classmethod
    def loadWidget(cls, name, baseinstance=None):
        if not name.endswith(cls.ui_extension):
            name += cls.ui_extension

        ref = resources.files(cls.ui_folder) / name
        with resources.as_file(ref) as path:
            return uic.loadUi(path, baseinstance)

    @classmethod
    def openData(cls, file):
        return resources.files(cls.data_folder).joinpath(file).open('r')


class Event:
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)


def displayError(title, message):
    error_message = QMessageBox()
    error_message.setIcon(QMessageBox.Critical)
    error_message.setWindowTitle(title)
    error_message.setText(message)
    error_message.exec()

