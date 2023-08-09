from enum import Enum

from src.models.arenaObjects.base import MultiArenaObject
from src.util import Color


class LightType(Enum):
    PointLight = 0
    WallLight = 1


LightColor = [Color.Red, Color.Green, Color.Blue, Color.Cyan, Color.Magenta, Color.Yellow]
LightTypes = [LightType.PointLight, LightType.WallLight]


class Light(MultiArenaObject):
    def getAttributes(self):
        attributes = super(Light, self).getAttributes()
        attributes.update({
            "color": Color.Red.name,
            "lightType": LightType.PointLight.name,
            "strength": 10,
        })
        return attributes

    @classmethod
    def dummyLight(cls):
        return Light({
            "strength": 0,
        })

    @staticmethod
    def strengthToRadius(strength):
        return int(strength * 5)

    @staticmethod
    def strengthToHeight(strength):
        return int(strength * 3)
