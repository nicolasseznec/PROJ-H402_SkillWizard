from src.util import Event


class Behavior:
    def __init__(self, data):
        self.skills = []  # Skill ids related to this behavior
        self.parameters = {}
        self.active = False  # whether the behavior is used by an active skill
        self.onActived = Event()

        self.loadFromData(data)

    def setActive(self, active):
        self.active = active
        self.onActived(active)

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.skills = data["skills"]
        self.description = data.get("desc", "")
        for param in data["parameters"]:
            name = param["name"]
            if name in self.parameters:
                self.parameters[name].loadFromData(param)
            else:
                parameter = None
                if param["type"] == "color":
                    parameter = BpColor(param)
                elif param["type"] == "int":
                    parameter = BpInt(param)
                elif param["type"] == "float":
                    parameter = BpFloat(param)

                if parameter is not None:
                    self.parameters[name] = parameter

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "skills": self.skills,
            "parameters": [p.toJson() for p in self.parameters.values()],
        }

    def reset(self):
        for param in self.parameters.values():
            param.reset()


class BehaviorParameter:
    def __init__(self, data):
        self.loadFromData(data)

    def loadFromData(self, data):
        self.name = data["name"]
        self.type = data["type"]
        self.description = "" if "desc" not in data else data["desc"]

    def update(self, values):
        pass

    def toJson(self):
        pass

    def reset(self):
        pass

# ------------- Behavior Parameters ---------------


class BpColor(BehaviorParameter):
    def loadFromData(self, data):
        super(BpColor, self).loadFromData(data)
        self.color = 0 if "color" not in data else data["color"]

    def update(self, values):
        self.color = values["color"]

    def toJson(self):
        return {
            "name": self.name,
            "type": "color",
            "color": self.color
        }

    def reset(self):
        self.color = 0


class BpInt(BehaviorParameter):
    def loadFromData(self, data):
        super(BpInt, self).loadFromData(data)
        self.value = 0 if "value" not in data else data["value"]
        self.range = [] if "range" not in data else data["range"]

    def update(self, values):
        self.value = values["value"]

    def toJson(self):
        return {
            "name": self.name,
            "type": "int",
            "value": self.value
        }

    def reset(self):
        self.value = 0


class BpFloat(BpInt):
    pass
