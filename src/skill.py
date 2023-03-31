from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QPushButton

from src.util import ResourceLoader, Event


class Skill:
    def __init__(self, data):
        self.loadFromData(data)
        # TODO : parameters
        self.active = False
        self.behaviours = []

    def setActive(self, active):
        # print(self.name, "->", active)
        self.active = active

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
        }

    def linkBehaviour(self, behaviour_id):
        self.behaviours.append(behaviour_id)


class SkillParameter:
    pass

    def __init__(self):
        # Range of parameters, distribution
        # Resolution
        # Accuracy
        # Response time
        pass


class SkillView:
    def __init__(self):
        self.skillItem = ResourceLoader.loadWidget("Skillitem.ui")  # TODO : try not to load the resource each time ?
        self.inspector = ResourceLoader.loadWidget("Skillinspector.ui")
        self.inspectorLayout = self.inspector.layout()
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


class SkillController:
    def __init__(self, skill):
        self.skill = skill
        self.skillView = SkillView()
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
