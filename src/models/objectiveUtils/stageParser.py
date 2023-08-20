"""
Stage Code Parser
"""
import json
from lark import Lark, Transformer

from src.util import ResourceLoader


class StageParser(Lark):
    def __init__(self, functionPath, grammarPath, **options):

        with ResourceLoader.openData(functionPath) as functionFile:
            functionData = json.load(functionFile)

        with ResourceLoader.openData(grammarPath) as grammarFile:
            grammar = grammarFile.read()

        self.transformer = CppTransformer(functionData)
        super().__init__(grammar, parser='lalr', transformer=self.transformer, **options)

    def getFunctions(self):
        return self.transformer.functions

    def getVariables(self):
        return self.transformer.variables


class CppTransformer(Transformer):
    tempVarIndex = 0

    def __init__(self, data):
        super().__init__()
        self.retrieveData(data)

    def retrieveData(self, data):
        self.variables = {v["name"]: v for v in data["variables"]}
        self.functions = {self.getKeyFromFunction(f["call"], f["arguments"]): f for f in data["functions"]}
        self.types = {t["name"]: t["code"] for t in data["types"]}

    # ------------ Rules ----------------
    # ---- Functions ----

    def func(self, children):
        function, arguments = children
        funcKey = self.getKeyFromFunction(function, [arg.valueType for arg in arguments])
        data = self.functions[funcKey]  # TODO : key check
        returnType = data["return"]

        argCode = ""
        first = True
        for arg in arguments:
            if not first:
                argCode += ", "
            first = False
            argCode += arg.instruction

        tempVar = self.createTempVar()
        code = self.getCode(*arguments)
        code += f"  {self.types[returnType]} {tempVar} = {function}({argCode});\n"

        return StageNode("func", returnType, value=function, children=arguments, data=data, instruction=tempVar, code=code)

    def args(self, arguments):
        return arguments

    # ---- Values ----

    def number(self, n):
        (n, ) = n
        return StageNode("number", "Real", value=float(n), instruction=str(n))

    def string(self, s):
        (s,) = s
        return StageNode("string", "String", value=str(s), instruction=str(s))

    def var(self, v):
        (v,) = v
        data = self.variables.get(v, {"name": "None", "type": "Pos"})   # TODO : look if defined in table of var and get its data
        return StageNode("var", data["type"], value=v, instruction=v, data=data)

    # ---- Operations ----

    def add(self, children):
        return self.operation("add", "+", children)

    def sub(self, children):
        return self.operation("sub", "-", children)

    def mul(self, children):
        return self.operation("mul", "*", children)

    def div(self, children):
        return self.operation("div", "/", children)

    def neg(self, v):
        (v,) = v
        valueType = v.valueType
        code = self.getCode(v)
        instruction = f"-{v.instruction}"
        return StageNode("neg", valueType, children=[v], code=code, instruction=instruction)

    def operation(self, name, operator, children):
        left, right = children
        valueType = left.valueType
        # verify types are the same
        code = self.getCode(left, right)
        instruction = f"({left.instruction} {operator} {right.instruction})"
        return StageNode(name, valueType, children=children, code=code, instruction=instruction)

    # ------------ Utils ----------------
    @staticmethod
    def getCode(*args):
        code = ""
        for arg in args:
            if arg.code:
                code += arg.code
        return code

    @staticmethod
    def getKeyFromFunction(function, arguments):
        key = function
        for arg in arguments:
            key += "_" + arg
        return key

    @classmethod
    def createTempVar(cls):
        cls.tempVarIndex += 1
        return f"tempVar_{cls.tempVarIndex}"


class StageNode:
    def __init__(self, rule, valueType, value=None, children=None, data=None, instruction=None, code=None):
        self.rule = rule  # (var, number, func, ...)
        self.valueType = valueType  # type of return (Real, Pos, List)
        self.value = value  # if string or number, raw value

        if children is None:
            children = []
        self.children = children

        if data is None:
            data = {}
        self.data = data

        self.code = code  # generated code so far for the stage
        if instruction is None:
            instruction = str(value)
        self.instruction = instruction  # current instruction

    def getVariables(self):
        variables = set()
        if self.rule == "var":
            variables.add(self.data["name"])
        for child in self.children:
            variables.update(child.getVariables())
        return variables

    def getFunctions(self):
        functions = set()
        if self.rule == "func":
            functions.add(self.data["call"])
        for child in self.children:
            functions.update(child.getFunctions())
        return functions

    def assignToStage(self, stage):
        self.code += f"  {stage} = {self.instruction};\n"
        self.instruction = stage

    def __str__(self):
        out = f"StageNode({self.rule}, {self.valueType}, {self.value})"
        for child in self.children:
            out += "\n  " + str(child)
        return out
