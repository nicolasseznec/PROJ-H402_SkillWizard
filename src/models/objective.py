from src.models.objectiveUtils.stage import Stage


class Objective:
    def __init__(self, data=None):
        if data is None:
            data = {}

        self.name = "New objective"
        self.postStepStages = []
        self.postExpStages = []
        self.initStages = []

        if data:
            self.loadFromData(data)

    def loadFromData(self, data):
        self.name = data.get("name", self.name)
        if "postStepStages" in data:
            self.postStepStages = [Stage(stage) for stage in data["postStepStages"]]
        if "postExpStages" in data:
            self.postExpStages = [Stage(stage) for stage in data["postExpStages"]]
        if "initStages" in data:
            self.initStages = [Stage(stage) for stage in data["initStages"]]

    def toJson(self):
        return {
            "name": self.name,
            "postStepStages": [stage.toJson() for stage in self.postStepStages],
            "postExpStages": [stage.toJson() for stage in self.postExpStages],
            "initStages": [stage.toJson() for stage in self.initStages],
        }
