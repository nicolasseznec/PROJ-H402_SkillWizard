from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget

from src.util import ResourceLoader, Event


# TODO : see how to generalize similarities with Skills


class Behaviour:
    def __init__(self, data):
        self.skills = []  # Skill ids related to this behaviour
        self.parameters = []
        self.loadFromData(data)
        self.active = False  # whether the behaviour is used by an active skill

    def setActive(self, active):
        self.active = active

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.skills = data["skills"]
        self.parameters.clear()
        for param in data["parameters"]:
            parameter = None
            if param["type"] == "color":
                parameter = BpColor(param)  # TODO : switch depending on type

            if parameter is not None:
                self.parameters.append(parameter)

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "skills": self.skills,
            "parameters": [p.toJson() for p in self.parameters],
        }


class BehaviourView:
    def __init__(self):
        self.behaviourItem = ResourceLoader.loadWidget("BehaviourItem.ui")
        self.setActive(False)
        self.inspector = ResourceLoader.loadWidget("BehaviourInspector.ui")
        self.inspectorLayout = self.inspector.scrollAreaWidgetContents.layout()
        self.inspectorLayout.setAlignment(Qt.AlignTop)
        self.baseItemColor = self.behaviourItem.palette().color(QPalette.Window)
        self.onSelected = Event()

        self.connectButtons()

    def updateView(self, behaviour):
        self.behaviourItem.LabelButton.setText(behaviour.name)
        self.inspector.BehaviourName.setText(behaviour.name)

    def connectButtons(self):
        self.behaviourItem.LabelButton.clicked.connect(self.labelClicked)

    def labelClicked(self):
        self.onSelected()

    def getCenterWidget(self):
        return self.inspector

    def setSelected(self, selected):
        if selected:
            self.setItemColor(QColor("lightgray"))
        else:
            self.setItemColor(self.baseItemColor)

    def setItemColor(self, color):
        palette: QPalette = self.behaviourItem.palette()
        palette.setColor(QPalette.Window, color)
        self.behaviourItem.setPalette(palette)

    def setActive(self, active):
        self.behaviourItem.setEnabled(active)

    def setHighlighted(self, highlighted):
        if highlighted:
            self.behaviourItem.setStyleSheet("QFrame {\n	border: 2px solid blue;\n}")
        else:
            self.behaviourItem.setStyleSheet("")

    def addParameter(self, view):
        self.inspectorLayout.addWidget(view)


class BehaviourController:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.behaviourView = BehaviourView()

        self.parameterControllers = []
        self.createParameterControllers()

        self.behaviourView.updateView(behaviour)
        self.behaviourView.onSelected += self.onSelected
        self.onBehaviourSelected = Event()

    def getView(self):
        return self.behaviourView

    def onSelected(self):
        self.onBehaviourSelected(self)

    def setActive(self, active):
        self.behaviour.setActive(active)
        # TODO : update view
        self.behaviourView.setActive(active)

    def setSelected(self, selected):
        self.behaviourView.setSelected(selected)

    def loadFromData(self, data):
        self.behaviour.loadFromData(data)
        # for param, controller in zip(self.behaviour.parameters, self.parameterControllers):
        #     controller.loadParameter(param)
        for controller in self.parameterControllers:
            for param in self.behaviour.parameters:
                if param.name == controller.parameter.name:
                    controller.loadParameter(param)

    def setHighlighted(self, highlighted):
        self.behaviourView.setHighlighted(highlighted)

    def createParameterControllers(self):
        for param in self.behaviour.parameters:
            controller = BehaviourParameterController(param)
            self.parameterControllers.append(controller)
            self.behaviourView.addParameter(controller.view)


class BehaviourParameter:
    def __init__(self, data):
        self.loadFromData(data)

    def loadFromData(self, data):
        self.name = data["name"]
        self.type = data["type"]

    def update(self, values):
        pass

    def toJson(self):
        pass


class BehaviourParameterView(QWidget):
    def __init__(self, parameter):
        super(BehaviourParameterView, self).__init__()
        self.loadWidget(parameter)

        self.blockChangeSignal = False
        self.onParameterChanged = Event()

        self.updateView(parameter)
        self.connectView()

    def updateView(self, parameter):
        self.blockChangeSignal = True
        self.setValues(parameter)
        self.blockChangeSignal = False

    def onValueChanged(self):
        if self.blockChangeSignal:
            return
        self.onParameterChanged()

    def connectView(self):
        pass  # value onchanged connect onValueChanged

    def loadWidget(self, parameter):
        pass
        # ResourceLoader.loadWidget("ParameterInspector.ui", self)
        # self.setTitle(parameter.name)

    def getValues(self):
        pass  # return values in dict

    def setValues(self, parameter):
        pass  # set values from parameter


class BehaviourParameterController:
    def __init__(self, parameter):
        self.parameter = parameter

        if parameter.type == "color":
            self.view = BpColorView(parameter)  # TODO : switch depending on type
        else:
            self.view = BehaviourParameterView(parameter)

        self.view.onParameterChanged += self.updateParameter

    def updateParameter(self):
        self.parameter.update(self.view.getValues())

    def loadParameter(self, parameter):
        self.parameter = parameter
        self.view.updateView(parameter)


# ------------- Behaviour Parameters ---------------

class BpColor(BehaviourParameter):
    def loadFromData(self, data):
        super(BpColor, self).loadFromData(data)
        self.color = 0 if "color" not in data else data["color"]

    def update(self, values):
        self.color = values["color"]
        print(self.color)

    def toJson(self):
        return {
            "name": self.name,
            "type": "color",
            "color": self.color
        }


class BpColorView(BehaviourParameterView):
    def connectView(self):
        self.color.currentIndexChanged.connect(self.onValueChanged)

    def loadWidget(self, parameter):
        ResourceLoader.loadWidget("BpColorInspector.ui", self)
        self.name.setText(parameter.name)

    def getValues(self):
        return {
            "color": self.color.currentIndex()
        }

    def setValues(self, parameter):
        self.color.setCurrentIndex(parameter.color)
