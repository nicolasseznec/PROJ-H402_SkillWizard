from PyQt5.QtWidgets import QWidget, QToolButton, QListWidget

from src.util import Event
from src.views.utils.itemList import SingleItemListView


class StageView(QWidget):
    def __init__(self, container, *__args):
        super().__init__(*__args)
        self.loadWidget()
        self.stageListView = self.createStageListView(container)

        self.onStageChanged = Event()
        self.CodeArea.textChanged.connect(self.codeAreaChanged)

        self.clear()
        self.blockSignals = False

    def loadWidget(self):
        pass

    def createStageListView(self, container):
        return StageListView(container)

    def updateView(self, stage):
        self.blockSignals = True
        self.StageName.setText('<html><head/><body><p><span style=" font-size:11pt;">{}</span></p></body></html>'.format(stage.name))
        self.CodeArea.setPlainText(stage.code)
        self.blockSignals = False
        self.setEnabled(True)

    def clear(self):
        self.StageName.setText("")
        self.CodeArea.setPlainText("")
        self.setEnabled(False)

    # ---------- Events ------------

    def codeAreaChanged(self):
        self.onStageChanged(code=self.CodeArea.toPlainText())


# --------------------------

class StageListView(SingleItemListView):
    def __init__(self, settingsContainer):
        self.settingsContainer = settingsContainer
        addButton, removeButton, listWidget = self.getWidgets(settingsContainer)
        super().__init__(addButton, removeButton, listWidget)

    def getWidgets(self, settingsContainer):
        return QToolButton(), QToolButton(), QListWidget()
