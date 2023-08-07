from importlib import resources
from enum import Enum
import uuid

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog


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

    def clear(self):
        self.__handlers.clear()


class DataContainer:
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.loadFromData(data)

    def loadFromData(self, data):
        attributes = self.getAttributes()
        for attribute in attributes:
            value = getattr(self, attribute, attributes[attribute]) if attribute not in data else data[attribute]
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


class Color(Enum):
    Red = 1
    Green = 2
    Blue = 3
    Cyan = 4
    Magenta = 5
    Yellow = 6
    Black = 7
    Gray = 8
    White = 9


def createMessage(title, message):
    dialog = QMessageBox()
    dialog.setWindowTitle(title)
    dialog.setText(message)
    return dialog


def displayError(title, message):
    dialog = createMessage(title, message)
    dialog.setIcon(QMessageBox.Critical)
    dialog.exec()


def displayInformation(title, message):
    dialog = createMessage(title, message)
    dialog.setIcon(QMessageBox.Information)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()


def generateUuid():
    return uuid.uuid4()


def generateItems(data, itemFactory):
    for item in data:
        yield itemFactory(item)


def containsAny(container, *args):
    return any(element in container for element in args)


def getOpenFileName(caption, fileFilter):
    file_dialog = QFileDialog()
    return file_dialog.getOpenFileName(None, caption=caption, filter=fileFilter)[0]


def getSaveFileName(caption, fileFilter):
    file_dialog = QFileDialog()
    return file_dialog.getSaveFileName(None, caption=caption, filter=fileFilter)[0]
