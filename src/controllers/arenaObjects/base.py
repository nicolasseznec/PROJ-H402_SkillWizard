from src.controllers.utils.itemList import ItemListController
from src.models.arenaObjects.base import BaseArenaObject
from src.util import Event, Shape, containsAny
from src.views.arenaObjects.base import BaseArenaObjectView, MultiArenaObjectView


class BaseArenaObjectController:
    """
    Base Controller for an arena object.
    """
    def __init__(self, model: BaseArenaObject, view: BaseArenaObjectView):
        self.model = model
        self.view = view
        self.view.onItemChanged += self.onViewChanged
        self.updateView()

    def updateView(self):
        """
        Update the content of the view to the model
        """
        self.view.updateView(self.model)

    # ---------- Events ------------

    def onViewChanged(self, **kwargs):
        """
        Called when the view has been modified.
        """
        self.model.loadFromData(kwargs)

        dimensions = self.model.toJson()
        if containsAny(kwargs, "width", "height", "orientation"):
            self.view.updateShapes(Shape.Rectangle, **dimensions)
        if containsAny(kwargs, "radius"):
            self.view.updateShapes(Shape.Circle, **dimensions)
        if containsAny(kwargs, "x"):
            self.view.setX(kwargs["x"])
        if containsAny(kwargs, "y"):
            self.view.setY(kwargs["y"])

    def setArenaPath(self, arenaPath):
        self.view.setArenaPath(arenaPath)


class MultiArenaObjectController(BaseArenaObjectController):
    """
    Controller for an arena object that can be put in a list.
    """
    def __init__(self, model, view: MultiArenaObjectView):
        super().__init__(model, view)
        self.view.onSelected += self.onViewSelected
        self.onSelected = Event()

    def handleRemoval(self):
        self.onSelected.clear()
        self.view.disconnectSettings()

    def setSelected(self, selected):
        self.view.setSelected(selected)

    def setName(self, text):
        self.model.name = text

    def setTabFocus(self, focus):
        self.view.setTabFocus(focus)

    def addToArena(self, arena):
        pass

    def removeFromArena(self, arena):
        pass

    # ---------- Events ------------

    def onViewSelected(self):
        self.onSelected(self)


# ------------ Item Lists --------------


class ArenaTabController:
    """
    Base class for a tab controller
    """
    def __init__(self, index, *args, **kwargs):
        self.index = index
        self.setTabFocus(False)

    def tabChanged(self, index):
        self.setTabFocus(self.index == index)

    def setTabFocus(self, focus):
        pass


class ArenaListController(ItemListController, ArenaTabController):
    """
    Base controller for a list of arena objects. See ItemListController
    """
    def __init__(self, view, index):
        super().__init__(view)
        ArenaTabController.__init__(self, index)
        self.onItemLoaded = Event()
        self.onItemUnloaded = Event()

    def unselectAll(self, controller=None):
        """
        Unselect all items except the given controller.
        """
        for item in self.itemsControllers:
            if item is controller:
                continue
            item.setSelected(False)

    def setTabFocus(self, focus):
        """
        Set the focus of every item to the given value (true or false)
        """
        for item in self.itemsControllers:
            item.setTabFocus(focus)

        index = self.view.getCurrentIndex()
        if focus and index >= 0:
            self.selectItem(index)

    def setArenaPath(self, arenaPath):
        for item in self.itemsControllers:
            item.setArenaPath(arenaPath)

    def loadArena(self, arena):
        """
        Loads the items from the given arena. Override in subclasses.
        """
        pass

    def loadItems(self, items):
        """
        Create the controller from a list of loaded items.
        """
        self.clear()
        for item in items:
            view = self.view.createNewItem()
            controller = self.createNewController(item, view)
            self.view.addItem(view, item.name)
            self.itemsControllers.append(controller)
            self.onItemLoaded(controller)

    def createNewController(self, model, view):
        """
        Called when an item is added to create its controller.
        """
        controller = self.controllerFactory(model, view)
        controller.onSelected += self.onControllerSelected
        return controller

    def controllerFactory(self, model, view):
        """
        Return a new item controller instance. Override in subclasses.
        """
        pass

    def handleRemoval(self, controller):
        """
        Handle the removal of a specific controller.
        """
        controller.onSelected -= self.onControllerSelected
        controller.handleRemoval()

    def clear(self):
        for item in self.itemsControllers:
            self.onItemUnloaded(item)
        super(ArenaListController, self).clear()

    # ---------- Events ------------

    def onControllerSelected(self, controller):
        index = self.itemsControllers.index(controller)
        self.onItemSelected(controller)
        self.view.selectRow(index)
        controller.updateView()

    def selectItem(self, index):
        self.itemsControllers[index].setSelected(True)

    # ----------------------

    def addItem(self):
        self.unselectAll()
        super(ArenaListController, self).addItem()

    def removeItem(self, index):
        super(ArenaListController, self).removeItem(index)

