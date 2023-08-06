from src.models.arenaObjects.base import MultiArenaObject
from src.util import Color


FloorColor = [Color.Black, Color.Gray, Color.White]


class Floor(MultiArenaObject):
    def getAttributes(self):
        attributes = super(Floor, self).getAttributes()
        attributes.update({
            "color": Color.Black.name,
        })
        return attributes
