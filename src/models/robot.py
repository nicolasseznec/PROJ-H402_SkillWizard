from src.util import DataContainer


class RobotModel(DataContainer):
    """
    Robot Reference model
    """
    def __init__(self, data):
        self.model = "None"
        self.inputs = None
        self.outputs = None

        super(RobotModel, self).__init__(data)

        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []

    def getAttributes(self):
        return {
            "model": "None",
            "name": "None",
            "desc": "[...]",
            "inputs": None,
            "outputs": None,
        }

    def toJson(self):
        return self.model
