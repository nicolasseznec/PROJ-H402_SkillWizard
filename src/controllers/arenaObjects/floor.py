from src.controllers.arenaObjects.base import MultiArenaObjectController, ArenaListController
from src.models.arenaObjects.floor import Floor


class FloorController(MultiArenaObjectController):
    pass


class FloorListController(ArenaListController):
    def controllerFactory(self, model, view):
        return FloorController(model, view)

    def createNewItem(self):
        return Floor()

    def getDefaultName(self):
        return "New Floor"
