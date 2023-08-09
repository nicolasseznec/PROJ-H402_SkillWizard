from src.controllers.arenaObjects.floor import FloorListController
from src.controllers.arenaObjects.light import LightListController
from src.controllers.arenaObjects.obstacle import ObstacleListController
from src.controllers.arenaObjects.spawn import SpawnController
from src.util import Event
from src.views.arena import ArenaView


class ArenaListControllerHandler:
    def __init__(self, lists):
        self.lists = lists
        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemLoaded = Event()
        self.onItemUnloaded = Event()
        self.connectEvents()

    def connectEvents(self):
        for elements in self.lists:
            elements.onItemAdded += self.onItemAdded
            elements.onItemRemoved += self.onItemRemoved
            elements.onItemLoaded += self.onItemLoaded
            elements.onItemUnloaded += self.onItemUnloaded
            elements.onItemSelected += self.onItemSelected

    def onItemSelected(self, controller):
        for elements in self.lists:
            elements.unselectAll(controller)

    def tabChanged(self, index):
        for elements in self.lists:
            elements.tabChanged(index)

    def updateViews(self, arena):
        for elements in self.lists:
            elements.loadArena(arena)

    def setArenaPath(self, arenaPath):
        for elements in self.lists:
            elements.setArenaPath(arenaPath)


class ArenaController:
    def __init__(self, view: ArenaView):
        self.view = view
        self.view.onArenaClicked += self.onArenaClicked
        self.view.onArenaSettingsChanged += self.onSettingsChanged
        self.view.onArenaTabChanged += self.onTabChanged
        self.view.onArenaPathChanged += self.onArenaPathChanged

        self.spawn = SpawnController(self.view.spawnView, 0)
        self.view.addSceneItem(self.spawn.view)
        self.listHandler = ArenaListControllerHandler([
            FloorListController(self.view.floorListView, 1),
            ObstacleListController(self.view.obstacleListView, 2),
            LightListController(self.view.lightListView, 3),
        ])
        self.listHandler.onItemAdded += self.onItemAdded
        self.listHandler.onItemRemoved += self.onItemRemoved
        self.listHandler.onItemLoaded += self.onItemLoaded
        self.listHandler.onItemUnloaded += self.onItemUnloaded

        self.onSelected = Event()

    def getCenterWidget(self):
        return self.view.getCenterWidget()

    # ---------- Events ------------

    def onArenaClicked(self):
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        if self.arena is not None:
            self.arena.loadFromData(kwargs)

    def onArenaPathChanged(self, arenaPath):
        self.listHandler.setArenaPath(arenaPath)
        self.spawn.setArenaPath(arenaPath)

    def onTabChanged(self, index):
        self.spawn.tabChanged(index)
        self.listHandler.tabChanged(index)

    def onItemAdded(self, controller):
        controller.addToArena(self.arena)
        self.onItemLoaded(controller)

    def onItemLoaded(self, controller):
        controller.setArenaPath(self.view.getArenaPath())
        self.view.addSceneItem(controller.view)

    def onItemRemoved(self, controller):
        controller.removeFromArena(self.arena)
        self.onItemUnloaded(controller)

    def onItemUnloaded(self, controller):
        self.view.removeSceneItem(controller.view)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setArena(self, arena):
        self.arena = arena

        if arena is not None:
            self.spawn.setSpawn(arena.spawn)
            self.listHandler.updateViews(arena)
            self.view.updateView(arena)
            self.onArenaPathChanged(self.view.getArenaPath())
