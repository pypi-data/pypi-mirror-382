from .util.core.preprocess import parseRule
from .util.core.formula import initFormula
from .util.core.solution_search import greedyFirstSearch
from .util.core.translate import translateCondition
from .util.core.simplify import simplifyConditon

def findStepFrameCondition(rule:str):
    rule = parseRule(rule)
    formula = initFormula(rule)
    result = greedyFirstSearch(formula)
    finalForm = result[0][-1]
    result = translateCondition(finalForm,result[2])
    result = simplifyConditon(result)
    return result


def getLogs(rule:str):
    rule = parseRule(rule)
    formula = initFormula(rule)
    result = greedyFirstSearch(formula)
    return result[1],result[2]