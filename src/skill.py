from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QPushButton, QGroupBox

from src.util import ResourceLoader, Event


class Skill:
    def __init__(self, data):
        self.behaviours = []
        self.parameters = []
        self.loadFromData(data)
        self.active = False

    def setActive(self, active):
        # print(self.name, "->", active)
        self.active = active

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.parameters.clear()
        for param in data["parameters"]:
            self.parameters.append(SkillParameter(param))

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "parameters": [p.toJson() for p in self.parameters],
        }

    def linkBehaviour(self, behaviour_id):
        self.behaviours.append(behaviour_id)


class SkillView:
    def __init__(self):
        self.skillItem = ResourceLoader.loadWidget("Skillitem.ui")  # TODO : try not to load the resource each time ?
        self.inspector = ResourceLoader.loadWidget("Skillinspector.ui")
        self.inspectorLayout = self.inspector.scrollAreaWidgetContents.layout()
        self.inspectorLayout.setAlignment(Qt.AlignTop)

        self.baseColor = self.skillItem.palette().color(QPalette.Window)
        self.baseItemColor = self.baseColor

        self.onSelected = Event()
        self.onAdded = Event()

        self.connectButtons()

        self.selected = False

    def updateView(self, skill):
        self.skillItem.LabelButton.setText(skill.name)
        self.inspector.SkillName.setText(skill.name)

    def connectButtons(self):
        self.skillItem.LabelButton.clicked.connect(self.labelClicked)
        self.skillItem.CheckBox.clicked.connect(self.checkBoxClicked)

    def labelClicked(self):
        self.onSelected()

    def checkBoxClicked(self, checked):
        self.onAdded(checked)

    def getCenterWidget(self):
        return self.inspector

    def setChecked(self, checked):
        self.skillItem.CheckBox.setChecked(checked)

        if checked:
            self.baseItemColor = QColor("gray")
        else:
            self.baseItemColor = self.baseColor

        if not self.selected:
            self.setItemColor(self.baseItemColor)

    def setSelected(self, selected):
        self.selected = selected
        if selected:
            self.setItemColor(QColor("lightgray"))
        else:
            self.setItemColor(self.baseItemColor)

    def setItemColor(self, color):
        palette: QPalette = self.skillItem.palette()
        palette.setColor(QPalette.Window, color)
        self.skillItem.setPalette(palette)

    def addParameter(self, view):
        self.inspectorLayout.addWidget(view)


class SkillController:
    def __init__(self, skill):
        self.skill = skill
        self.skillView = SkillView()
        self.parameterControllers = []
        self.createParameterControllers()
        self.skillView.updateView(skill)

        self.skillView.onSelected += self.onSelected
        self.skillView.onAdded += self.onAdded

        self.onSkillSelected = Event()
        self.onSkillAdded = Event()

    def getView(self):
        return self.skillView

    def onSelected(self):
        self.onSkillSelected(self)
        # print("Clicked : ", self.skill.name)

    def onAdded(self, checked):
        self.setChecked(checked)
        self.skill.setActive(checked)
        self.onSkillAdded(self.skill, checked)
        # TODO : visual feedback

    def setChecked(self, checked):
        self.skillView.setChecked(checked)

    def setSelected(self, selected):
        self.skillView.setSelected(selected)

    def createParameterControllers(self):
        for param in self.skill.parameters:
            controller = SkillParameterController(param)
            self.parameterControllers.append(controller)
            self.skillView.addParameter(controller.view)

    def loadFromData(self, data):
        self.skill.loadFromData(data)
        for param, controller in zip(self.skill.parameters, self.parameterControllers):
            controller.loadParameter(param)


class SkillParameter:
    # TODO : extensible attribute handling
    def __init__(self, data, attributes=None):
        self.attributes = attributes if attributes is not None else \
            ["name", "resolution", "accuracy", "responseTime"]

        self.loadFromData(data)

    def loadFromData(self, data):
        for attribute in self.attributes:
            value = 0 if attribute not in data else data[attribute]
            setattr(self, attribute, value)

    def toJson(self):
        return {attribute: getattr(self, attribute) for attribute in self.attributes}


class SkillParameterView(QGroupBox):
    def __init__(self, parameter):
        super().__init__()
        ResourceLoader.loadWidget("ParameterInspector.ui", self)
        self.setTitle(parameter.name)
        self.blockChangeSignal = False

        self.onParameterChanged = Event()

        self.updateView(parameter)
        self.Resolution.valueChanged.connect(self.onValueChanged)
        self.Accuracy.valueChanged.connect(self.onValueChanged)
        self.ResponseTime.valueChanged.connect(self.onValueChanged)

    def updateView(self, parameter):
        self.blockChangeSignal = True
        self.Resolution.setValue(parameter.resolution)
        self.Accuracy.setValue(parameter.accuracy)
        self.ResponseTime.setValue(parameter.responseTime)
        self.blockChangeSignal = False

    def onValueChanged(self):
        if self.blockChangeSignal:
            return
        self.onParameterChanged()


class SkillParameterController:
    def __init__(self, parameter):
        self.parameter = parameter
        self.view = SkillParameterView(parameter)
        self.view.onParameterChanged += self.updateParameter

    def updateParameter(self):
        self.parameter.resolution = self.view.Resolution.value()
        self.parameter.accuracy = self.view.Accuracy.value()
        self.parameter.responseTime = self.view.ResponseTime.value()

    def loadParameter(self, parameter):
        self.parameter = parameter
        self.view.updateView(parameter)
