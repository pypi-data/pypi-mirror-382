PARAMETER_NAMES = {
    "" : "input", "input" : "input", "i" : "input",
    "a" : "advanced", "advanced" : "advanced",
    "n" : "noWarnings", "nowarnings" : "noWarnings", "nw" : "noWarnings", "nowarn" : "nowarnings",
    "b" : "breakdown", "breakdown" : "breakdown",
    "s0" : "s0", "s1" : "s0", "s1.0" : "s0", "s1.5" : "s0", "s2" : "s0", "s2.0" : "s0", "s2.5" : "s0",
    "s3" : "s3", "s3.0" : "s3", "s3.5" : "s3",
}

class Parameters:
    advanced = False
    noWarnings = False
    breakdown = False
    season = 3.5

def splitParameters(inputString, warnings):
    while "---" in inputString:
        inputString = inputString.replace("---", "--")
    inputString = "-- " + inputString

    sequence = ""
    params = Parameters()

    for parameterString in inputString.split("--"):
        parameter = parameterString.split(" ")[0].lower()
        value = " ".join(parameterString.split(" ")[1:])

        if not parameter in PARAMETER_NAMES:
            warnings += [f"{parameter} is not a recognised parameter"]
            sequence += value
            continue

        if PARAMETER_NAMES[parameter] == "input":
            sequence += str(value)

        if PARAMETER_NAMES[parameter] == "advanced":
            params.advanced = True
            sequence += value # this parameter takes no arguments - parse as regular input

        if PARAMETER_NAMES[parameter] == "noWarnings":
            params.noWarnings = True
            sequence += value # this parameter takes no arguments - parse as regular input

        if PARAMETER_NAMES[parameter] == "breakdown":
            params.breakdown = True
            sequence += value # this parameter takes no arguments - parse as regular input

        if PARAMETER_NAMES[parameter] == "s0":
            params.season = 0
            sequence += value # this parameter takes no arguments - parse as regular input
        
        if PARAMETER_NAMES[parameter] == "s3":
            params.season = 3
            sequence += value # this parameter takes no arguments - parse as regular input

    return sequence, params