from ...AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...AST.core.ast_util import getSpecificNodes,toInfix
from ..errors.errors import InferenceError
from .nominal_rules import NominalInference
from .adjunction_rules import AdjunctionInference


def processFormulaWithAST(formula: str) -> list[str]:
    """Process a formula using an Abstract Syntax Tree (AST) to extract specific nodes.
    This function builds an AST from the given formula and retrieves all nodes that match
    the specified condition (in this case, nodes with the '<' operator).

    Args:
        formula (str): The formula to process, which should be a valid string representation

    Raises:
        InferenceError: If the AST cannot be built from the formula or if no nodes with the '<' operator are found.
        InferenceError: If no '<' nodes are found in the AST.

    Returns:
        list[str]: A list of strings representing the infix notation of the subtrees/nodes that 
        match the condition.
        Each string corresponds to a node/subtree in the AST that contains the '<' operator.
    """
    tree = AbstractSyntaxTree()
    tree.buildTree(formula)
    
    if tree.root is None:
        raise InferenceError("Failed to build AST from formula")
    
    nodes = getSpecificNodes(tree.root, "<")
    if not nodes:
        raise InferenceError("No '<' nodes found in AST")
    
    infixStrings = [toInfix(i) for i in nodes]

    return infixStrings


def inferenceRules(formula: str) -> tuple[dict[str, list[str]], dict[str, dict[str, str]]]:
    """
    Get all inference rules for a given formula.

    Runs the nominal and adjunction inference engines and returns:
        - a dictionary mapping subformulae (formulas/statements with `<`) 
        to lists of applicable inference rules, and
        - a dictionary tracking which rules are applied.

    Args:
        formula (str): The formula to process.

    Returns:
        A tuple containing:
            - dict[str, list[str]]: A mapping of each subformula to the
                list of inference rules applicable to it.
            - dict[str, dict[str, str]]: A mapping that tracks which
                inference rules are applied to which subformulae.
    """

    formulae = processFormulaWithAST(formula)
    inferenceEngignes = [NominalInference(),AdjunctionInference()]
    resultDict = {i:[] for i in formulae}
    trackRules = {i:{} for i in formulae}

    for engine in inferenceEngignes:
        for form in resultDict.keys():
            availableInferenceRules = engine.get_inferences(form)
            availableRules = engine.get_applicable_rules(form)

            for i in range(len(availableInferenceRules)):
                trackRules[form][availableInferenceRules[i]]=availableRules[i]
                
            resultDict[form].extend(availableInferenceRules)
    
    return (resultDict,trackRules)


if __name__=="__main__":
    formula = "#x<i(y)=>#x<#y"
    inferenceRules(formula)