from src.controllers.arenaObjects.base import MultiArenaObjectController, ArenaListController
from src.models.arenaObjects.obstacle import Obstacle


class ObstacleController(MultiArenaObjectController):
    pass


class ObstacleListController(ArenaListController):
    def controllerFactory(self, model, view):
        return ObstacleController(model, view)

    def createNewItem(self):
        return Obstacle()

    def getDefaultName(self):
        return "New Obstacle"
