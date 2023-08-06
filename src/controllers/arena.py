from src.util import Event


class ArenaController:
    def __init__(self, view):
        self.view = view
        self.view.onArenaClicked = self.onArenaClicked
        self.view.onArenaSettingsChanged += self.onSettingsChanged

        self.onSelected = Event()

    def getCenterWidget(self):
        return self.view.getCenterWidget()

    # ---------- Events ------------

    def onArenaClicked(self):
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        if self.arena is not None:
            self.arena.loadFromData(kwargs)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setArena(self, arena):
        self.arena = arena

        if arena is not None:
            self.view.updateView(arena)
