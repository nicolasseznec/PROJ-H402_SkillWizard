from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget

from src.util import ResourceLoader, Event


class BehaviorView:
    """
    View for a behavior inspector and the item in the side panel.
    """
    def __init__(self):
        self.behaviorItem = ResourceLoader.loadWidget("BehaviorItem.ui")
        self.inspector = ResourceLoader.loadWidget("BehaviorInspector.ui")
        self.inspectorLayout = self.inspector.scrollAreaWidgetContents.layout()
        self.inspectorLayout.setAlignment(Qt.AlignTop)
        self.baseItemColor = self.behaviorItem.palette().color(QPalette.Window)

        self.onSelected = Event()
        self.connectButtons()
        self.setActive(False)

    def updateView(self, behavior):
        """
        Update the view's contents from a given behavior.
        """
        self.behaviorItem.LabelButton.setText(behavior.name)
        self.inspector.BehaviorName.setText(behavior.name)
        self.inspector.description.setText(behavior.description)
        self.setActive(behavior.active)

    def connectButtons(self):
        self.behaviorItem.LabelButton.clicked.connect(self.labelClicked)

    def labelClicked(self):
        """
        Called when the behavior is selected in the side pnel
        """
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
    """
    Base view for a generic behavior parameter.
    """
    def __init__(self, parameter):
        super(BehaviorParameterView, self).__init__()
        self.loadWidget(parameter)

        self.blockSignal = False
        self.onParameterChanged = Event()

        self.updateView(parameter)
        self.connectView()

    def updateView(self, parameter):
        """
        Update the content of the view to the given parameter.
        """
        self.blockSignal = True
        self.setValues(parameter)
        self.blockSignal = False

    def onValueChanged(self):
        """
        Called when a value in the view has been modified.
        """
        if self.blockSignal:
            return
        self.onParameterChanged()

    def connectView(self):
        """
        Connect the signals to onValueChanged
        """
        pass

    def loadWidget(self, parameter):
        """
        Loads the view widget. See ResourceLoader.loadWidget(self.uiFile, self)
        """
        pass

    def getValues(self):
        """
        Returns all values of the view in a dict.
        """
        pass

    def setValues(self, parameter):
        """
        Set the content of the view to the given parameter.
        """
        pass


# ------------- Behavior Parameters ---------------

class BpColorView(BehaviorParameterView):
    """
    View for a color behavior parameter.
    """
    def connectView(self):
        self.color.currentIndexChanged.connect(self.onValueChanged)

    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("behaviors/BpColorInspector.ui", self)
        self.name.setText(parameter.name)
        self.description.setText(parameter.description)

    def getValues(self):
        return {
            "color": self.color.currentIndex()
        }

    def setValues(self, parameter):
        self.color.setCurrentIndex(parameter.color)


class BpIntView(BehaviorParameterView):
    """
    View for an integer behavior parameter.
    """
    def connectView(self):
        self.value.valueChanged.connect(self.onValueChanged)

    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("behaviors/BpIntInspector.ui", self)
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
    """
    View for a float behavior parameter
    """
    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("behaviors/BpFloatInspector.ui", self)
        self.setupWidget(parameter)
