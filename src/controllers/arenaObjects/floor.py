from src.controllers.arenaObjects.base import MultiArenaObjectController, ArenaListController
from src.models.arenaObjects.floor import Floor


class FloorController(MultiArenaObjectController):
    def addToArena(self, arena):
        arena.floors.append(self.model)

    def removeFromArena(self, arena):
        arena.floors.remove(self.model)


class FloorListController(ArenaListController):
    def controllerFactory(self, model, view):
        return FloorController(model, view)

    def createNewItem(self):
        return Floor()

    def getDefaultName(self):
        return "New Floor"

    def loadArena(self, arena):
        self.loadItems(arena.floors)
