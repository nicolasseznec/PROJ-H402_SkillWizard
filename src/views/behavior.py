from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget

from src.util import ResourceLoader, Event


class BehaviorView:
    def __init__(self):
        self.behaviorItem = ResourceLoader.loadWidget("BehaviourItem.ui")
        self.inspector = ResourceLoader.loadWidget("BehaviourInspector.ui")
        self.inspectorLayout = self.inspector.scrollAreaWidgetContents.layout()
        self.inspectorLayout.setAlignment(Qt.AlignTop)
        self.baseItemColor = self.behaviorItem.palette().color(QPalette.Window)

        self.onSelected = Event()
        self.connectButtons()
        self.setActive(False)

    def updateView(self, behavior):
        self.behaviorItem.LabelButton.setText(behavior.name)
        self.inspector.BehaviourName.setText(behavior.name)
        self.inspector.description.setText(behavior.description)
        self.setActive(behavior.active)

    def connectButtons(self):
        self.behaviorItem.LabelButton.clicked.connect(self.labelClicked)

    def labelClicked(self):
        self.onSelected()

    def getCenterWidget(self):
        return self.inspector

    def getSideWidget(self):
        return self.behaviorItem

    def setSelected(self, selected):
        if selected:
            self.setItemColor(QColor("lightgray"))
        else:
            self.setItemColor(self.baseItemColor)

    def setItemColor(self, color):
        palette: QPalette = self.behaviorItem.palette()
        palette.setColor(QPalette.Window, color)
        self.behaviorItem.setPalette(palette)

    def setActive(self, active):
        self.behaviorItem.setEnabled(active)

    def setHighlighted(self, highlighted):
        if highlighted:
            self.behaviorItem.setStyleSheet("QFrame {\n	border: 2px solid blue;\n}")
        else:
            self.behaviorItem.setStyleSheet("")

    def addParameter(self, view):
        self.inspectorLayout.addWidget(view)


class BehaviorParameterView(QWidget):
    def __init__(self, parameter):
        super(BehaviorParameterView, self).__init__()
        self.loadWidget(parameter)

        self.blockSignal = False
        self.onParameterChanged = Event()

        self.updateView(parameter)
        self.connectView()

    def updateView(self, parameter):
        self.blockSignal = True
        self.setValues(parameter)
        self.blockSignal = False

    def onValueChanged(self):
        if self.blockSignal:
            return
        self.onParameterChanged()

    def connectView(self):
        pass  # value onchanged connect onValueChanged

    def loadWidget(self, parameter):
        pass  # ResourceLoader.loadWidget(self.uiFile, self)

    def getValues(self):
        pass  # return values in dict

    def setValues(self, parameter):
        pass  # set values from parameter


# ------------- Behavior Parameters ---------------

class BpColorView(BehaviorParameterView):
    def connectView(self):
        self.color.currentIndexChanged.connect(self.onValueChanged)

    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("BpColorInspector.ui", self)
        self.name.setText(parameter.name)
        self.description.setText(parameter.description)

    def getValues(self):
        return {
            "color": self.color.currentIndex()
        }

    def setValues(self, parameter):
        self.color.setCurrentIndex(parameter.color)


class BpIntView(BehaviorParameterView):
    def connectView(self):
        self.value.valueChanged.connect(self.onValueChanged)

    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("BpIntInspector.ui", self)
        self.setupWidget(parameter)

    def setupWidget(self, parameter):
        self.name.setText(parameter.name)
        self.description.setText(parameter.description)
        if parameter.range:
            self.value.setRange(parameter.range[0], parameter.range[1])

    def getValues(self):
        return {
            "value": self.value.value()
        }

    def setValues(self, parameter):
        self.value.setValue(parameter.value)


class BpFloatView(BpIntView):
    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("BpFloatInspector.ui", self)
        self.setupWidget(parameter)
