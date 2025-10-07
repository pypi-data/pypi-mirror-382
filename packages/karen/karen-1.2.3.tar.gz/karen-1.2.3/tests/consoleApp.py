from karen.evaluate import evaluate
from karen.getCombo import *
from karen.parameters import *

while True:

    rawInput = input(">> ") + " " # space added so that commands with no arguments are easily handled
    while len(rawInput) > 0 and rawInput[0] in " !":
        rawInput = rawInput[1:]
    print("")

    if len(rawInput) > 4 and rawInput[:5] == "help ":
        print("!eval [combo]: evaluates the given combo")
        print("!exit : closes the terminal")

    elif len(rawInput) > 4 and rawInput[:5] == "eval ":
        warnings = []
        inputString, params = splitParameters(rawInput[5:], warnings)
        evaluate(inputString, params, warnings).printToConsole()

    elif len(rawInput) > 5 and rawInput[:6] == "combo ":
        warnings = []
        inputString, params = splitParameters(rawInput[6:], warnings)
        getCombo(inputString, params, warnings).printToConsole()

    elif len(rawInput) > 5 and rawInput[:7] == "combos ":
        warnings = []
        inputString, params = splitParameters(rawInput[7:], warnings)
        listCombos(inputString, params, warnings).printToConsole()

    elif len(rawInput) > 4 and rawInput[:5] == "exit ":
        break

    else:
        print("Command not recognised, use '!help' to see a list of commands")

    print("\n")