class Skill:
    def __init__(self, data):
        self.behaviors = []
        self.parameters = {}
        self.active = False
        self.loadFromData(data)

    def setActive(self, active):
        self.active = active

    def loadFromData(self, data):
        self.name = data["name"]
        self.id = data["id"]
        for param in data["parameters"]:
            name = param["name"]
            if name in self.parameters:
                self.parameters[name].loadFromData(param)
            else:
                self.parameters[name] = SkillParameter(param)

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "parameters": [p.toJson() for p in self.parameters.values()],
        }

    def linkBehavior(self, behavior_id):
        self.behaviors.append(behavior_id)

    def reset(self):
        self.active = False
        for param in self.parameters.values():
            param.reset()


class SkillParameter:
    # TODO : extensible attribute handling
    def __init__(self, data, attributes=None):
        self.attributes = attributes if attributes is not None else \
            ["name", "resolution", "accuracy", "responseTime"]

        self.loadFromData(data)

    def loadFromData(self, data):
        for attribute in self.attributes:
            value = 0 if attribute not in data else data[attribute]
            setattr(self, attribute, value)

    def toJson(self):
        return {attribute: getattr(self, attribute) for attribute in self.attributes}

    def reset(self):
        for attribute in self.attributes:
            if attribute != "name":
                setattr(self, attribute, 0)
