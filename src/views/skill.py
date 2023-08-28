from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGroupBox

from src.util import ResourceLoader, Event


class SkillView:
    """
    View for a skill inspector and the item in the side panel.
    """
    def __init__(self):
        self.skillItem = ResourceLoader.loadWidget("Skillitem.ui")
        self.inspector = ResourceLoader.loadWidget("Skillinspector.ui")
        self.inspectorLayout = self.inspector.scrollAreaWidgetContents.layout()
        self.inspectorLayout.setAlignment(Qt.AlignTop)
        self.connectButtons()
        self.blockSignal = False
        self.selected = False
        self.baseColor = self.skillItem.palette().color(QPalette.Window)
        self.baseItemColor = self.baseColor

        self.onSelected = Event()
        self.onChecked = Event()

    def connectButtons(self):
        self.skillItem.LabelButton.clicked.connect(self.labelClicked)
        self.skillItem.CheckBox.clicked.connect(self.checkBoxClicked)

    def updateView(self, skill):
        """
        Update the view's contents from a given skill.
        """
        self.skillItem.LabelButton.setText(skill.name)
        self.inspector.SkillName.setText(skill.name)
        self.blockSignal = True
        self.setChecked(skill.active)
        self.blockSignal = False

    # ---------- Events ------------

    def labelClicked(self):
        """
        Called when the skill is selected in the side pnel
        """
        if not self.blockSignal:
            self.onSelected()

    def checkBoxClicked(self, checked):
        """
        Called when the skill checkbox is clicked in the side pnel
        """
        if not self.blockSignal:
            self.onChecked(checked)

    # -----------------------------

    def getCenterWidget(self):
        return self.inspector

    def getSideWidget(self):
        return self.skillItem

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


class SkillParameterView(QGroupBox):
    """
    Base view for a generic skill parameter.
    """
    def __init__(self, parameter):
        super().__init__()
        ResourceLoader.loadWidget("ParameterInspector.ui", self)
        self.setTitle(parameter.name)
        self.blockSignal = False

        self.onParameterChanged = Event()

        self.updateView(parameter)
        self.Resolution.valueChanged.connect(self.onValueChanged)
        self.Accuracy.valueChanged.connect(self.onValueChanged)
        self.ResponseTime.valueChanged.connect(self.onValueChanged)

    def updateView(self, parameter):
        self.blockSignal = True
        self.Resolution.setValue(parameter.resolution)
        self.Accuracy.setValue(parameter.accuracy)
        self.ResponseTime.setValue(parameter.responseTime)
        self.blockSignal = False

    def onValueChanged(self):
        if self.blockSignal:
            return
        self.onParameterChanged()
