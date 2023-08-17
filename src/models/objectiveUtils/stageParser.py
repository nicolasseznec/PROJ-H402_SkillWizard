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

        super().__init__(grammar, parser='lalr', transformer=CppTransformer(functionData), **options)


class CppTransformer(Transformer):
    def __init__(self, functionData):
        super().__init__()
        self.data = functionData
