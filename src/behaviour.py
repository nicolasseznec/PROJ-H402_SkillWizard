from PyQt5.QtGui import QPalette, QColor

from src.util import ResourceLoader, Event
# TODO : see how to generalize similarities with Skills


class Behaviour:
    def __init__(self, data):
        self.skills = []  # Skill ids related to this behaviour
        self.loadFromData(data)
        # TODO : parameters
        self.active = False  # whether the behaviour is used by an active skill

    def setActive(self, active):
        self.active = active

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.skills = data["skills"]

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "skills": self.skills,
        }


class BehaviourView:
    def __init__(self):
        self.behaviourItem = ResourceLoader.loadWidget("BehaviourItem.ui")
        self.setActive(False)
        self.inspector = ResourceLoader.loadWidget("BehaviourInspector.ui")
        self.inspectorLayout = self.inspector.layout()
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


class BehaviourController:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.behaviourView = BehaviourView()
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

    def setHighlighted(self, highlighted):
        self.behaviourView.setHighlighted(highlighted)