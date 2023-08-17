from src.util import DataContainer


class Stage(DataContainer):
    def getAttributes(self):
        return {
            "name": "stage",
            "increment": True,
            "code": "",
        }

    @staticmethod
    def getNameFromIndex(index):
        return "stage{}".format(index)
