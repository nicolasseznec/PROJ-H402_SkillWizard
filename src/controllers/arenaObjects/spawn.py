from src.controllers.arenaObjects.base import BaseArenaObjectController, ArenaTabController
from src.models.arenaObjects.spawn import ArenaSpawn
from src.views.arenaObjects.spawn import SpawnView


class SpawnController(BaseArenaObjectController, ArenaTabController):
    """
    Controller for the spawn area object.
    """
    def __init__(self, view: SpawnView, index):
        self.model = ArenaSpawn()
        super().__init__(self.model, view)
        ArenaTabController.__init__(self, index)

    def setSpawn(self, spawn):
        self.model = spawn
        self.updateView()

    def setTabFocus(self, focus):
        self.view.setTabFocus(focus)
