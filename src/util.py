from importlib import resources
from enum import Enum

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


class DataContainer:
    def __init__(self, data):
        self.loadFromData(data)

    def loadFromData(self, data):
        attributes = self.getAttributes()
        for attribute in attributes:
            value = attributes[attribute] if attribute not in data else data[attribute]
            setattr(self, attribute, value)

    def toJson(self):
        return {attribute: getattr(self, attribute) for attribute in self.getAttributes()}

    def getAttributes(self):
        return {}


class Shape(Enum):
    Square = 1
    Hexagon = 2
    Octagon = 3
    Dodecagon = 4
    Circle = 5
    Rectangle = 6


def displayError(title, message):
    error_message = QMessageBox()
    error_message.setIcon(QMessageBox.Critical)
    error_message.setWindowTitle(title)
    error_message.setText(message)
    error_message.exec()

