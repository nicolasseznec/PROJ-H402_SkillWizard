from collections import defaultdict


class Mission:
    """
    Model for a mission (selected skills, behaviours, objective function and other parameters)
    """
    def __init__(self, skills, behaviors, data=None):
        self.skills = skills
        self.behaviors = behaviors
        self.behaviorsLinks = defaultdict(int)
        self.model_data = None
        self.reference_model = None
        # self.arena = Arena(data)

        if data is not None:
            self.loadFromData(data)

    def toJson(self):
        return {
            "Skills": [s.toJson() for s in self.skills if s.active],
            "Behaviors": [b.toJson() for b in self.behaviors if b.active],
            # "Arena": self.arena.toJson(),
            "ReferenceModel": self.reference_model.toJson(),
        }

    def setModel(self, model):
        self.reference_model = model

    # ------------ Loading Data ----------------

    def loadFromData(self, data):
        # TODO : checks for data validity
        self.loadSkills(data["Skills"])
        self.loadBehaviors(data["Behaviors"])
        # TODO : load robot model

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
