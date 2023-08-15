from collections import defaultdict

from src.models.arena import Arena
from src.models.objective import Objective


class Mission:
    """
    Model for a mission (selected skills, behaviours, objective function and other parameters)
    """
    def __init__(self, skills, behaviors, referenceModels, data=None):
        if data is None:
            data = {}

        self.skills = skills
        self.behaviors = behaviors
        self.behaviorsLinks = defaultdict(int)
        self.referenceModels = referenceModels
        self.referenceModel = next(iter(self.referenceModels.values()))
        self.arena = Arena(data.get("Arena", None))
        self.objective = Objective(data.get("Objective", None))

        if data:
            self.loadFromData(data)

    def toJson(self):
        return {
            "Skills": [s.toJson() for s in self.skills.values() if s.active],
            "Behaviors": [b.toJson() for b in self.behaviors.values() if b.active],
            "Arena": self.arena.toJson(),
            "ReferenceModel": self.referenceModel.toJson(),
            "Objective": self.objective.toJson()
        }

    def setModel(self, model):
        self.referenceModel = model

    # ------------ Loading Data ----------------

    def loadFromData(self, data):
        # TODO : checks for data validity
        self.loadSkills(data["Skills"])
        self.loadBehaviors(data["Behaviors"])
        self.loadReferenceModel(data["ReferenceModel"])

    def loadSkills(self, data):
        for item in data:
            skill_id = item["id"]
            if skill_id not in self.skills:
                continue

            skill = self.skills[skill_id]
            skill.loadFromData(item)
            self.enableSkill(skill)

    def loadBehaviors(self, data):
        for item in data:
            behavior_id = item["id"]
            if behavior_id not in self.behaviors:
                continue

            behavior = self.behaviors[behavior_id]
            behavior.loadFromData(item)

    def loadReferenceModel(self, reference):
        if reference in self.referenceModels:
            self.referenceModel = self.referenceModels[reference]
        else:
            self.referenceModel = next(iter(self.referenceModels.values()))

    # ------------ Enabling/Disabling Skills ----------------

    def enableSkill(self, skill):
        self.skills[skill.id].setActive(True)

        for b_id in skill.behaviors:
            self.behaviorsLinks[b_id] += 1
            if self.behaviorsLinks[b_id] == 1:
                self.behaviors[b_id].setActive(True)

    def disableSkill(self, skill):
        self.skills[skill.id].setActive(False)

        for b_id in skill.behaviors:
            self.behaviorsLinks[b_id] -= 1
            if self.behaviorsLinks[b_id] <= 0:
                self.behaviors[b_id].setActive(False)
