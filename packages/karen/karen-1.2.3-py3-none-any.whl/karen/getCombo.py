from karen.evaluate import evaluate
from karen.classify import *
from karen.combo import simplify, inputStringToSequence
from karen.output import Output
from karen.parameters import Parameters

def getCombo(name, params=Parameters(), warnings=[]):
    comboSequence = getComboSequence(name)
    if comboSequence == "":
        return Output(error="Combo not found")
    return evaluate(comboSequence, params=params, warnings=warnings)
        
def listCombos(inputString="", params=Parameters(), warnings=[]):

    # resolve the initial sequence
    comboSequence = inputStringToSequence(inputString, warnings) + [""]
    initialSequence = "".join(comboSequence)
    reducedSequence = initialSequence.replace("j", "").replace("d", "").replace("l", "").replace("a", "s")
    simpleSequence = "".join(simplify(comboSequence))
    reducedSimpleSequence = simpleSequence.replace("j", "").replace("d", "").replace("l", "").replace("a", "s")

    if len(COMBO_SEQUENCES) == 0:
        loadComboSequences()
    comboList = []
    sequenceList = []
    maxLength = 0

    for combo in COMBO_SEQUENCES:
        if len(COMBO_SEQUENCES[combo]) >= len(reducedSequence) and COMBO_SEQUENCES[combo][:len(reducedSequence)] == reducedSequence:
            comboList += [combo]
            sequenceList += [initialSequence + COMBO_SEQUENCES[combo][len(reducedSequence):]]
            maxLength = max(maxLength, len(comboList[-1]))
        elif len(COMBO_SEQUENCES[combo]) >= len(reducedSimpleSequence) and COMBO_SEQUENCES[combo][:len(reducedSimpleSequence)] == reducedSimpleSequence:
            comboList += [combo]
            sequenceList += [simpleSequence + COMBO_SEQUENCES[combo][len(reducedSimpleSequence):]]
            maxLength = max(maxLength, len(comboList[-1]))

    title = "Karen Combo List"
    description = "" if reducedSequence == "" else f"Requirement: starts with \"{initialSequence}\""
    block = "\n".join([comboList[i] + " " * (maxLength - len(comboList[i])) + " | " + sequenceList[i] for i in range(len(comboList))])

    if block == "":
        return Output(error=f"No documented combos begin with {initialSequence}")

    return Output(title=title, description=description, block=block, warnings=warnings)