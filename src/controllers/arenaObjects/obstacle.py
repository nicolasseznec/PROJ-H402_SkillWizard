from src.controllers.arenaObjects.base import MultiArenaObjectController, ArenaListController
from src.models.arenaObjects.obstacle import Obstacle


class ObstacleController(MultiArenaObjectController):
    """
    Controller for an obstacle object
    """
    def addToArena(self, arena):
        arena.obstacles.append(self.model)

    def removeFromArena(self, arena):
        arena.obstacles.remove(self.model)


class ObstacleListController(ArenaListController):
    def controllerFactory(self, model, view):
        return ObstacleController(model, view)

    def createNewItem(self):
        return Obstacle()

    def getDefaultName(self):
        return "New Obstacle"

    def loadArena(self, arena):
        self.loadItems(arena.obstacles)
