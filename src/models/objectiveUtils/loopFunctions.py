"""
Loop Functions Generation utilities
"""
from os.path import splitext
from collections import defaultdict
from string import Template

from src.models.objectiveUtils.stageParser import StageParser
from src.util import ResourceLoader, cleanIdentifier


# Remaining Template tags
# ----- H -------
# private_variables

# ----- CPP ------
# init_function
# reset_function
# post_experiment_function


def generateLoopFunctions(mission, filePath, **options):
    content = defaultdict(str)

    basePath = splitext(filePath)[0]  # Get the file path without extension
    cppPath = f"{basePath}.cpp"
    hPath = f"{basePath}.h"
    cppRawTemplate, hRawTemplate = getTemplates("TemplateLoopFunction.cpp", "TemplateLoopFunction.h")
    cppTemplate = Template(cppRawTemplate)
    hTemplate = Template(hRawTemplate)

    parser = StageParser("objective_model.json", "objective_stage.lark")

    objective = mission.objective

    content.update(getObjectiveNames(objective.name))
    content["compute_step_function"] = generatePostStepCode(objective.postStepStages, parser)

    with open(cppPath, 'w') as file:
        file.write(cppTemplate.substitute(content))
    with open(hPath, 'w') as file:
        file.write(hTemplate.substitute(content))


# -----------------------------------------------------------------------------

def getTemplates(*files):
    outputs = []
    for file in files:
        with ResourceLoader.openData(file) as template:
            outputs.append(template.read())

    return outputs


def getObjectiveNames(name):
    name = cleanIdentifier(name)
    return {
        "objective_name": name,
        "OBJECTIVE_NAME": name.upper(),
        "objective_name_lower": name.lower()
    }


# -----------------------------------------------------------------------------

def generatePostStepCode(stages, parser):
    code = "Real temp = 0;\n"

    for stage in stages:
        stageVar = cleanIdentifier(stage.name)
        code += f"\n  Real {stageVar} = 0;\n"

        if not stage.code:
            continue

        parsedCode = parser.parse(stage.code, on_error=onParsingError)
        # code += parsedCode
        print(parsedCode.pretty())

        if stage.increment:
            code += f"  temp += {stageVar};\n"

    code += "\n  return temp;"
    return code


def onParsingError(error):
    print(error)
    return False
