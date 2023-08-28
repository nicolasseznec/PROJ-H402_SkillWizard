from src.controllers.arenaObjects.base import MultiArenaObjectController, ArenaListController
from src.models.arenaObjects.light import Light
from src.util import containsAny, Color


class LightController(MultiArenaObjectController):
    """
    Controller for a light object
    """
    def addToArena(self, arena):
        arena.lights.append(self.model)

    def removeFromArena(self, arena):
        arena.lights.remove(self.model)

    # ---------- Events ------------

    def onViewChanged(self, **kwargs):
        self.model.loadFromData(kwargs)

        dimensions = self.model.toJson()
        if containsAny(kwargs, "strength", "orientation", "width"):
            self.view.updateLights(**dimensions)
        if containsAny(kwargs, "color", "strength", "orientation"):
            self.view.updateColor(Color[self.model.color], **dimensions)


class LightListController(ArenaListController):
    def controllerFactory(self, model, view):
        return LightController(model, view)

    def createNewItem(self):
        return Light()

    def getDefaultName(self):
        return "New Light"

    def loadArena(self, arena):
        self.loadItems(arena.lights)
