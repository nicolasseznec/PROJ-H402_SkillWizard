from src.models.arenaObjects.floor import Floor
from src.models.arenaObjects.light import Light
from src.models.arenaObjects.obstacle import Obstacle
from src.models.arenaObjects.spawn import ArenaSpawn
from src.util import Shape

ArenaShape = [Shape(i) for i in range(1, 6)]


class Arena:
    def __init__(self, data=None):
        if data is None:
            data = {}

        self.shape = ArenaShape[0]
        self.sideLength = 1
        self.robotNumber = 1
        self.spawn = ArenaSpawn(data.get("spawn", None))
        self.obstacles = []
        self.floors = []
        self.lights = []

        if data:
            self.loadFromData(data)

    def loadFromData(self, data):
        self.shape = Shape[data.get("shape", self.shape.name)]
        self.sideLength = data.get("sideLength", self.sideLength)
        self.robotNumber = data.get("robotNumber", self.robotNumber)
        self.spawn.loadFromData(data.get("spawn", {}))

        if "floors" in data:
            self.floors = [Floor(floor) for floor in data["floors"]]
        if "obstacles" in data:
            self.obstacles = [Obstacle(obstacle) for obstacle in data["obstacles"]]
        if "lights" in data:
            self.lights = [Light(light) for light in data["lights"]]

    def toJson(self):
        return {
            "shape": self.shape.name,
            "sideLength": self.sideLength,
            "robotNumber": self.robotNumber,
            "spawn": self.spawn.toJson(),
            "floors": [f.toJson() for f in self.floors],
            "obstacles": [o.toJson() for o in self.obstacles],
            "lights": [li.toJson() for li in self.lights],
        }
