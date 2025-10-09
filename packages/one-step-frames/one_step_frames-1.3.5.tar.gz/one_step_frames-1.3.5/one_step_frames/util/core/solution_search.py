from .priority_stack import PriorityStack
from ..rules.inference_rules import inferenceRules
from ..rules.ackermann_rules import findVariables,applyAckermannRule,ackermannHeuristic


def greedyFirstSearch(formula: str) -> tuple[list[str], list[str], dict[str,str]]:
    """Perform a greedy first search on the formula to find a solution.
    A Priority stack is used with the ackermann heuristic 
    to prioritize items.

    Args:
        formula (str): The formula to search on.
        
    Returns:
        tuple: A tuple containing:
            - list[str]: The order of rules 
            - list[str]: Logging information
            - dict[str,str]: The corresponding rules index(Nominal rule 1, adjunction 1 etc)
    """
    variables = findVariables(formula)
    numberVariables = len(variables) 
    stillSearch = True
    iterations = 0

    trackState = []
    trackLog = []
    trackRules = {}
    
    #init
    trackRules[formula]="INIT"

    pq = PriorityStack()
    pq.push(0,formula)   

    while not pq.empty() and stillSearch and iterations<30:
        iterations+=1
        item = pq.pop()
        trackState.append(item)
        trackLog.append(f"Current formula:{item}")

        if (item==None):
            break

        currentVariables = findVariables(item)
        appliedAck = False

        # Goal test
        if len(currentVariables)==0:
            stillSearch = False
            trackLog.append(f"Goal found:{item}")
            continue
        
        #Check ackermann rule
        for var in variables:
            newForm = applyAckermannRule(item)

            if (newForm!= item):
                trackRules[newForm]="ACK"
                trackLog.append(f"Applying Ackermann rule to {item}, yielding {newForm}")
                pq.push(5,newForm)
                appliedAck = True
                break
        
        if appliedAck:
            continue
        
        # Do inference rules now
        currentInferenceRules,trackingRules = inferenceRules(item)

        for subform in currentInferenceRules.keys():
            for replacement in currentInferenceRules[subform]:
                tempFormula = item
                tempFormula = tempFormula.replace(subform,replacement)

                if (tempFormula.count("=>"))>1:
                    continue

                score = ackermannHeuristic(tempFormula,numberVariables)

                appliedInferenceRule = trackingRules[subform][replacement]
                trackRules[tempFormula]=appliedInferenceRule
                trackLog.append(f"Added potential formula {tempFormula} with priority {score}")

                pq.push(score,tempFormula)

    #Filter to only have the rules that leads to the solution
    trackRules = {k:v for k,v in trackRules.items() if k in trackState}

    return trackState,trackLog,trackRules

