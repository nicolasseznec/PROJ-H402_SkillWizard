from src.controllers.utils.itemList import ItemListController
from src.models.arenaObjects.base import BaseArenaObject
from src.util import Event, Shape, containsAny
from src.views.arenaObjects.base import BaseArenaObjectView, MultiArenaObjectView


class BaseArenaObjectController:
    def __init__(self, model: BaseArenaObject, view: BaseArenaObjectView):
        self.model = model
        self.view = view
        self.view.onItemChanged += self.onViewChanged
        self.updateView()

    def updateView(self):
        self.view.updateView(self.model)

    # ---------- Events ------------

    def onViewChanged(self, **kwargs):
        self.model.loadFromData(kwargs)

        dimensions = self.model.toJson()
        if containsAny(kwargs, "width", "height", "orientation"):
            self.view.updateShapes(Shape.Rectangle, **dimensions)
        if containsAny(kwargs, "radius"):
            self.view.updateShapes(Shape.Circle, **dimensions)

    def setArenaPath(self, arenaPath):
        self.view.setArenaPath(arenaPath)


class MultiArenaObjectController(BaseArenaObjectController):
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
    def __init__(self, index, *args, **kwargs):
        self.index = index

    def tabChanged(self, index):
        self.setTabFocus(self.index == index)

    def setTabFocus(self, focus):
        pass


class ArenaListController(ItemListController, ArenaTabController):
    def __init__(self, view, index):
        super().__init__(view)
        ArenaTabController.__init__(self, index)
        self.onItemLoaded = Event()
        self.onItemUnloaded = Event()

    def unselectAll(self, controller=None):
        for item in self.itemsControllers:
            if item is controller:
                continue
            item.setSelected(False)

    def setTabFocus(self, focus):
        for item in self.itemsControllers:
            item.setTabFocus(focus)

        index = self.view.getCurrentIndex()
        if focus and index >= 0:
            self.selectItem(index)

    def setArenaPath(self, arenaPath):
        for item in self.itemsControllers:
            item.setArenaPath(arenaPath)

    def loadArena(self, arena):
        pass

    def loadItems(self, items):
        self.clear()
        for item in items:
            view = self.view.createNewItem()
            controller = self.createNewController(item, view)
            self.view.addItem(view, item.name)
            self.itemsControllers.append(controller)
            self.onItemLoaded(controller)

    def createNewController(self, model, view):
        controller = self.controllerFactory(model, view)
        controller.onSelected += self.onControllerSelected
        return controller

    def controllerFactory(self, model, view):
        pass

    def handleRemoval(self, controller):
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
        # select new item ?

    def removeItem(self, index):
        super(ArenaListController, self).removeItem(index)
