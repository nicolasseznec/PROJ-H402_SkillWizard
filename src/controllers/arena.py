from src.controllers.arenaObjects.floor import FloorListController
from src.controllers.arenaObjects.light import LightListController
from src.controllers.arenaObjects.obstacle import ObstacleListController
from src.controllers.arenaObjects.spawn import SpawnController
from src.util import Event
from src.views.arena import ArenaView


class ArenaListControllerHandler:
    """
    Handle all the lists of arena objects (floors, obstacles, lights, ...)

    Connect and relays their events to the arena controller.
    """
    def __init__(self, lists):
        self.lists = lists
        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemLoaded = Event()
        self.onItemUnloaded = Event()
        self.connectEvents()

    def connectEvents(self):
        """
        Connects the handler to all the list events (add, remove, select, load, unload)
        """
        for elements in self.lists:
            elements.onItemAdded += self.onItemAdded
            elements.onItemRemoved += self.onItemRemoved
            elements.onItemLoaded += self.onItemLoaded
            elements.onItemUnloaded += self.onItemUnloaded
            elements.onItemSelected += self.onItemSelected

    def onItemSelected(self, controller):
        """
        Called before an item in one of the list is selected. Unselects every items
        """
        for elements in self.lists:
            elements.unselectAll(controller)

    def tabChanged(self, index):
        """
        Called when the tab is changed. Notifies every list (to change the focus).
        """
        for elements in self.lists:
            elements.tabChanged(index)

    def updateViews(self, arena):
        """
        Update the list to a new arena.
        """
        for elements in self.lists:
            elements.loadArena(arena)

    def setArenaPath(self, arenaPath):
        """
        Update the shape of the arena in all items.
        """
        for elements in self.lists:
            elements.setArenaPath(arenaPath)


class ArenaController:
    """
    Controller for the arena editor and its settings tab.
    """
    def __init__(self, view: ArenaView):
        self.view = view
        self.arena = None
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
        """
        Called when the user clicks on edit arena.
        """
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        """
        Called when one of the arena settings changed. All changed settings are given in kwargs. Updates the current
        arena with the new settings.
        """
        if self.arena is not None:
            self.arena.loadFromData(kwargs)

    def onArenaPathChanged(self, arenaPath):
        """
        Called when the shape of the arena has changed. Relays the new shape to all arena objects.
        """
        self.listHandler.setArenaPath(arenaPath)
        self.spawn.setArenaPath(arenaPath)

    def onTabChanged(self, index):
        """
        Called when the arena objects tab changes. Updates the focus of all arena objects.
        """
        self.spawn.tabChanged(index)
        self.listHandler.tabChanged(index)

    def onItemAdded(self, controller):
        """
        Called when a new arena object has been created.
        """
        controller.addToArena(self.arena)
        self.onItemLoaded(controller)

    def onItemLoaded(self, controller):
        """
        Called when an arena object has been loaded (from a mission file).
        """
        controller.setArenaPath(self.view.getArenaPath())
        self.view.addSceneItem(controller.view)

    def onItemRemoved(self, controller):
        """
        Called when an anera object has been deleted.
        """
        controller.removeFromArena(self.arena)
        self.onItemUnloaded(controller)

    def onItemUnloaded(self, controller):
        """
        Called when an arena object is unloaded (when the current mission changes)
        """
        self.view.removeSceneItem(controller.view)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setArena(self, arena):
        """
        Update all controllers (and their views) to a new arena.
        """
        self.arena = arena

        if arena is not None:
            self.spawn.setSpawn(arena.spawn)
            self.listHandler.updateViews(arena)
            self.view.updateView(arena)
            self.onArenaPathChanged(self.view.getArenaPath())
