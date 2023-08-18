"""
Loop Functions Generation utilities
"""
from os.path import splitext
from collections import defaultdict
from string import Template

from src.models.objectiveUtils.stageParser import StageParser, CppTransformer
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

    if "source" in options:
        content["source_header"] = generateSourceHeader(options["source"])

    functions = set()
    variables = set()
    content.update(getObjectiveNames(objective.name))
    content["compute_step_function"], postStepFuncs, postStepVars = generatePostStepCode(objective.postStepStages, parser)
    functions.update(postStepFuncs)
    variables.update(postStepVars)  # TODO : every var not defined in model needs to be in the private vars

    content["private_function_decl"], content["private_function_def"] = generateFunctionCode(functions, parser.getFunctions(), content["objective_name"])

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


def generateSourceHeader(source):
    return f"// File Generated from {source}"


def generateFunctionCode(functions, data, objective_name):
    declarations = ""
    definitions = "/********* Generated Functions **********/\n\n"

    # dependencies = set()
    # first scan to add all dependencies
    # for function in data.values():
    #     if function["call"] in functions and "requires" in function:
    #         functions.update(function["requires"])
    #
    # for function in data.values():
    #     if function["call"] in functions:
    #         declarations += "    " + function["declaration"]
    #         definitions += "\n" + function["definition"]
    #         if "requires" in function:
    #             functions.update(function["requires"])
    #
    for function in data.values():
        declarations += "    " + function["declaration"]
        definitions += "\n" + function["definition"]

    definitions = Template(definitions).substitute({
        "objective_name": objective_name
    })

    return declarations, definitions


# -----------------------------------------------------------------------------

def generatePostStepCode(stages, parser):
    code = "Real temp = 0;\n"
    CppTransformer.tempVarIndex = 0
    functions = set()
    variables = set()

    for stage in stages:
        stageVar = cleanIdentifier(stage.name)
        code += f"\n  Real {stageVar} = 0;\n"

        if not stage.code:
            continue

        stageNode = parser.parse(stage.code)
        stageNode.assignToStage(stageVar)  # TODO : verify final node is of type "Real"
        code += stageNode.code

        functions.update(stageNode.getFunctions())
        variables.update(stageNode.getVariables())

        if stage.increment:
            code += f"  temp += {stageVar};\n"

    code += "\n  return temp;"

    initialisation = ""
    varData = parser.getVariables()
    for var in variables:
        if var in varData:
            initialisation += varData[var]["code"]

    return initialisation + code, functions, variables
