from karen.state import State
from karen.combo import *
from karen.classify import classify
from math import floor
from karen.actions import *
from karen.output import Output
from karen.parameters import Parameters
from karen.logger import logCombo

def evaluate(inputString, params=Parameters(), warnings=[]):

    state = State(params)
    comboSequence = inputStringToSequence(inputString, warnings) + [""]

    # runs a second evaluation with maximum action ranges
    maxTravelTimeState = State(params)
    maxTravelTimeState.inferInitialState(comboSequence)

    # infer initial state being airborne/having overhead
    state.inferInitialState(comboSequence, warnings)
    comboSequence = state.correctSequence(comboSequence)

    if params.advanced == False:
        comboSequence = simplify(comboSequence)

    logCombo("".join(comboSequence))

    for i in range(len(comboSequence) - 1):
        nextAction = [j for j in comboSequence[i+1:] if not j in ["j", "d", "l"]][0]
        addAction(state, comboSequence[i], nextAction, params, warnings)
        addAction(maxTravelTimeState, comboSequence[i], nextAction, params, maxTravelTimes=True)
    state.resolve(warnings)
    maxTravelTimeState.resolve()

    # checks for continued burn tracer damage after final action
    burnTracerBonusDamage = ""
    if state.burnActiveTimer > 12:
        burnTracerBonusDamage = "(plus " + str(int(floor((state.burnActiveTimer - 1) / 12) * BURN_TRACER_DPS / 5)) +" burn over time)"

    comboName = classify("".join(comboSequence))

    timeSecondsMin = round(state.timeTaken / 60, 2)
    timeSecondsMax = round(maxTravelTimeState.timeTaken / 60, 2)
    showTimeRange = maxTravelTimeState.timeTaken != state.timeTaken and params.advanced
    timeSeconds = str(timeSecondsMin) + (f"-{timeSecondsMax}" if showTimeRange else "")
    timeFrames = str(state.timeTaken) + (f"-{maxTravelTimeState.timeTaken}" if showTimeRange else "")
    dpsMin = "NaN" if timeSecondsMax == 0 else str(int(round(state.damageDealt / timeSecondsMax, 0)))
    dpsMax = "NaN" if timeSecondsMin == 0 else str(int(round(state.damageDealt / timeSecondsMin, 0)))
    showDPS = params.advanced and dpsMax != "NaN"
    dps = "" if not showDPS else f", {dpsMin}{f"-{dpsMax}" if dpsMin != dpsMax else ""}dps"


    timeFromDamageSecondsMin = round(state.timeFromDamage / 60, 2)
    timeFromDamageSecondsMax = round(maxTravelTimeState.timeFromDamage / 60, 2)
    showTimeFromDamageRange = maxTravelTimeState.timeFromDamage != state.timeFromDamage and params.advanced
    timeFromDamageSeconds = str(timeFromDamageSecondsMin) + (f"-{timeFromDamageSecondsMax}" if showTimeFromDamageRange else "")
    timeFromDamageFrames = str(state.timeFromDamage) + (f"-{maxTravelTimeState.timeFromDamage}" if showTimeFromDamageRange else "")
    dpsFromDamageMin = "NaN" if timeFromDamageSecondsMax == 0 else str(int(round(state.damageDealt / timeFromDamageSecondsMax, 0)))
    dpsFromDamageMax = "NaN" if timeFromDamageSecondsMin == 0 else str(int(round(state.damageDealt / timeFromDamageSecondsMin, 0)))
    showDPSFromDamage = params.advanced and dpsFromDamageMax != "NaN"
    dpsFromDamage = "" if not showDPSFromDamage else f", {dpsFromDamageMin}{f"-{dpsFromDamageMax}" if dpsFromDamageMin != dpsFromDamageMax else ""}dps"

    description = ( 
    f"**Time:** {timeSeconds} seconds ({timeFrames} frames{dps})"
    f"{f"\n**Time From Damage:** {timeFromDamageSeconds} seconds ({timeFromDamageFrames} frames{dpsFromDamage})" if state.damageDealt > 0 else ""}"
    f"\n**Damage:** {int(state.damageDealt)} {burnTracerBonusDamage}" 
    )

    if params.noWarnings:
        warnings = []

    block = state.breakdown if params.breakdown else ""

    return Output(title=comboName, combo=state.sequence, description=description, block=block, warnings=warnings)