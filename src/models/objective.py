class Objective:
    def __init__(self, data=None):
        if data is None:
            data = {}

        self.name = "New objective"

        if data:
            self.loadFromData(data)

    def loadFromData(self, data):
        self.name = data.get("name", self.name)

    def toJson(self):
        return {"name": self.name}
