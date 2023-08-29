"""
Loop Functions Generation utilities
"""
from math import pi
from os.path import splitext
from collections import defaultdict
from string import Template

from src.models.objectiveUtils.stageParser import StageParser, CppTransformer
from src.util import ResourceLoader, cleanIdentifier, Shape, shape_scale_factor


def generateLoopFunctions(mission, filePath, **options):
    content = defaultdict(str)

    basePath = splitext(filePath)[0]
    cppPath = f"{basePath}.cpp"
    hPath = f"{basePath}.h"
    cppRawTemplate, hRawTemplate = getTemplates("TemplateLoopFunction.cpp", "TemplateLoopFunction.h")
    cppTemplate = Template(cppRawTemplate)
    hTemplate = Template(hRawTemplate)

    parser = StageParser("objective_model.json", "objective_grammar.lark")

    objective = mission.objective

    if "source" in options:
        content["source_header"] = generateSourceHeader(options["source"])

    functions = set()
    variables = set()
    content.update(getObjectiveNames(objective.name))

    content["compute_step_function"], postStepFuncs, postStepVars = generatePostStepCode(objective.postStepStages, parser)
    functions.update(postStepFuncs)
    variables.update(postStepVars)  # TODO : every var not defined in model needs to be in the private vars

    content["post_experiment_function"], postExpFuncs, postExpVars = generatePostExpCode(objective.postExpStages, parser)
    functions.update(postExpFuncs)
    variables.update(postExpVars)

    content["init_function"], content["private_variables"], initFuncs, initVars = generateInitCode(objective.initStages, parser)
    functions.update(initFuncs)
    variables.update(initVars)

    content["private_function_decl"], content["private_function_def"] = generateFunctionCode(functions, parser.getFunctions(), content["objective_name"])

    content["random_position_function"] = generateRandomPositionFunctionCode(mission.arena)

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
    declarations = "    /********* Generated Functions **********/\n\n"
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
        if function["declaration"]:
            declarations += "    " + function["declaration"]
        if function["definition"]:
            definitions += "\n" + function["definition"]

    definitions = Template(definitions).substitute({
        "objective_name": objective_name
    })

    return declarations, definitions


def generateVariableInitialisation(variables, varData):
    initialisation = ""
    for var in variables:
        if var in varData:
            initialisation += varData[var]["code"]
    return initialisation


# -----------------------------------------------------------------------------

def generateStageCode(stages, parser):
    initialisation = "Real temp = 0;\n"
    code = ""
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

    return initialisation, code, functions, variables


def generatePostStepCode(stages, parser):
    initialisation, code, functions, variables = generateStageCode(stages, parser)
    code += "\n  return temp;"
    varData = parser.getVariables()
    initialisation += generateVariableInitialisation(variables, varData)
    return initialisation + code, functions, variables


def generatePostExpCode(stages, parser):
    if True in [s.increment for s in stages]:  # at least one stage is used
        initialisation, code, functions, variables = generateStageCode(stages, parser)
        code += "\n  m_ObjectiveFunction = temp;"
        varData = parser.getVariables()
        initialisation += generateVariableInitialisation(variables, varData)
    else:
        initialisation, code, functions, variables = "", "", set(), set()
    return initialisation + code, functions, variables


def generateInitCode(stages, parser):
    code = ""
    CppTransformer.tempVarIndex = 0
    functions = set()
    variables = set()
    variableHeader = ""
    types = parser.getTypes()

    for variable in stages:
        varName = cleanIdentifier(variable.name)

        if not variable.code:
            continue

        stageNode = parser.parse(variable.code)
        stageNode.assignToStage(varName)
        code += stageNode.code
        variableHeader += f"    {types[stageNode.valueType]} {varName};\n"

        functions.update(stageNode.getFunctions())
        variables.update(stageNode.getVariables())

    varData = parser.getVariables()
    initialisation = generateVariableInitialisation(variables, varData)

    return initialisation + code, variableHeader, functions, variables


def generateRandomPositionFunctionCode(arena):
    code = "a = m_pcRng->Uniform(CRange<Real>(0.0f, 1.0f));\n  b = m_pcRng->Uniform(CRange<Real>(0.0f, 1.0f));\n"
    spawn = arena.spawn
    shape = Shape[spawn.shape]
    coord_scale = (arena.sideLength * shape_scale_factor[arena.shape]) / (240 * 100)

    x0 = spawn.x * coord_scale
    y0 = spawn.y * coord_scale

    if shape == Shape.Circle:
        code += "  if (b<a) {\n" \
                "    temp = a;\n" \
                "    a = b;\n" \
                "    b = temp;\n" \
                "  }\n"
        radius = spawn.radius * coord_scale
        code += f"  Real fPosX = b * {round(radius, 2)} * cos(2 * CRadians::PI.GetValue() * (a / b)) + {round(x0, 2)};\n"
        code += f"  Real fPosY = b * {round(radius, 2)} * sin(2 * CRadians::PI.GetValue() * (a / b)) + {round(y0, 2)};\n"

    elif shape == Shape.Rectangle:
        width = spawn.width * coord_scale
        height = spawn.height * coord_scale
        angle = round(spawn.orientation * pi/180, 3)
        code += f"  Real tempX = a * {round(width, 2)};\n"
        code += f"  Real tempY = b * {round(height, 2)};\n"
        code += f"  Real fPosX = cos({angle}) * tempX + sin({angle}) * tempY + {round(x0, 2)};\n"
        code += f"  Real fPosY = -sin({angle}) * tempX + cos({angle}) * tempY + {round(y0, 2)};\n"

    return code
