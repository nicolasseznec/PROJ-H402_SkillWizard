from src.util import DataContainer, Shape

ArenaObjectShape = [Shape.Circle, Shape.Rectangle]


class BaseArenaObject(DataContainer):
    def getAttributes(self):
        return {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
            "radius": 50,
            "shape": Shape.Circle.name,
            "orientation": 0,
        }


class MultiArenaObject(BaseArenaObject):
    def getAttributes(self):
        attributes = super(MultiArenaObject, self).getAttributes()
        attributes.update({
            "name": "new (model)",
        })
        return attributes
