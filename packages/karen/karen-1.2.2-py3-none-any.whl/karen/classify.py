CLASSIFICATIONS = {
    "tGu" : "Bread & Butter (BnB)",
    "tGuwtt" : "BnB Tracers",
    "tGuso" : "BnB Short Plink",
    "tGuwto" : "BnB Long Plink",
    "tGupt" : "BnB Punch",
    "tGutp" : "Reverse Panther",
    "tGuwpp+o" : "BnB U3H",
    "tGwtuwt" : "Weave Combo",
    "tGptu" : "Panther Combo",
    "tGsptu" : "Fast Panther",
    "tGsotu" : "Overhead Panther Combo",
    "tptu" : "One Two",
    "totu" : "Overhead One Two",
    "tgptu" : "Fishing Combo / Sekkombo",
    "tgotu" : "Reverse Yo-Yo",
    "tgktu" : "Grip Kick Rip (GKR)",
    "otG+u" : "Fast FFAmestack",
    "otuwtg" : "Overhead Burst",
    "otsptu" : "Master Manipulator",
    "otgwtu" : "Master Masher",
    "otgwtuwto" : "Fantastic Killer",
    "otuwtotgwtuwtoto" : "Further Beyond",
    "to+G+u" : "Saporen FFAmestack",
    "gwtuwto" : "Yo-Yo",
    "tguwto" : "Pre-Tag Yo-Yo",
    "tgwuwto" : "Pre-Tag Yo-Yo",
    "gwtuototu" : "Botched Yo-Yo",
    "gtutp" : "Agni-Kai Yo-Yo",
    "tuwtGu" : "Driveby",
    "twGuot" : "Bald Slam",
    "uwtGo" : "Vortex",
    "tgptsptu" : "Hydro Combo",
    "tptsptu" : "Alternate Hydro Combo",
    "o+tgstu" : "Evil Combo",

    "tGbu" : "Burn BnB / Fadeaway",
    "otbu" : "Burn Overhead Burst",
    "tgptbu" : "Fried Fish / Firehook",
    "tbuwtg" : "In And Out",
    "tptbu" : "Burn One Two",
    "tGbtu" : "Burn Weave",
    "tGwtbu" : "Burn Weave",
}

def classify(comboString):
    comboString = comboString.replace("j", "").replace("d", "").replace("l", "") # doesnt consider jumping/landing in classificaiton
    comboString = comboString.replace("a", "s") # autoswings are equivalent to swings for classification purposes

    if comboString in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString]
    
    # adding tracer to the end is considered the same combo
    if len(comboString) >= 1 and comboString[-1] == "t" and comboString[:-1] in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString[:-1]]
    if len(comboString) >= 2 and comboString[-2:] == "wt" and comboString[:-2] in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString[:-2]]
    
    # attempts classification assuming swing cancels are typos of whiff cancels
    if "st" in comboString:
        attempt = classify(comboString.replace("st", "wt")) 
        if attempt != "Undocumented":
            return "Wasteful " + attempt
    
    # attempts to classify as a slow variation of another combo by adding whiff cancels
    improveString = comboString.replace("ut", "uwt").replace("gt", "gwt").replace("ug", "uwg")
    if improveString != comboString:
        attempt = classify(improveString)
        if attempt != "Undocumented":
            return "Slow " + attempt
    
    return "Undocumented"

COMBO_SEQUENCES = {}

OVERRIDE_COMBO_SEQUENCES = {
    "Reverse Yo-Yo" : "tgdotu",
    "Further Beyond" : "otuwtotgwtuwtodto",
    "Yo-Yo" : "gdwtuwto",
    "Pre-Tag Yo-Yo" : "tgduwto",
    "Botched Yo-Yo" : "gdwtuototu",
    "Agni-Kai Yo-Yo" : "gdtutp",
    "Vortex" : "uwtdGo",
    "Hydro Combo" : "tgptaptu",
    "Alternate Hydro Combo" : "tptaptu",
    "Burn Weave" : "tGwtbu",
    "Evil Combo" : "o+tgatu",
}

COMBO_ALIASES = {
    "bnb" : "Bread & Butter (BnB)",
    "bnbplink" : "BnB Long Plink",
    "fishing" : "Fishing Combo / Sekkombo",
    "fish" : "Fishing Combo / Sekkombo",
    "sekkombo" : "Fishing Combo / Sekkombo",
    "sekombo" : "Fishing Combo / Sekkombo",
    "gripkickrip" : "Grip Kick Rip (GKR)",
    "gkr" : "Grip Kick Rip (GKR)",
    "ohburst" : "Overhead Burst",
    "fantastic" : "Fantastic Killer",
    "sapstack" : "Saporen FFAmestack",
    "agnikai" : "Agni-Kai Yo-Yo",
    "bald" : "Bald Slam",
    "skypull" : "Yo-Yo",
    "spc" : "Yo-Yo",
    "skyyoink" : "Yo-Yo",
    "preyoyo" : "Pre-Tag Yo-Yo",
    "tagyoyo" : "Pre-Tag Yo-Yo",
    "althydro" : "Alternate Hydro Combo",

    "burnbnb" : "Burn BnB / Fadeaway",
    "fadeaway" : "Burn BnB / Fadeaway",
    "burnohburst" : "Burn Overhead Burst",
    "burnoverhead" : "Burn Overhead Burst",
    "burnoh" : "Burn Overhead Burst",
    "friedfish" : "Fried Fish / Firehook",
    "fried" : "Fried Fish / Firehook",
    "burnsekkombo" : "Fried Fish / Firehook",
    "burnsekombo" : "Fried Fish / Firehook",
    "firehook" : "Fried Fish / Firehook",
    "innout" : "In And Out",
    "in&out" : "In And Out",
}

def loadComboSequences():
    for sequence in CLASSIFICATIONS:
        COMBO_SEQUENCES[CLASSIFICATIONS[sequence]] = sequence
    for combo in OVERRIDE_COMBO_SEQUENCES:
        COMBO_SEQUENCES[combo] = OVERRIDE_COMBO_SEQUENCES[combo]

    for sequence in CLASSIFICATIONS:
        filterName = CLASSIFICATIONS[sequence].replace(" ", "").replace("-", "").lower()
        if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]
        COMBO_ALIASES[filterName] = CLASSIFICATIONS[sequence]

    for name in COMBO_ALIASES.copy():
        if "bnb" in name:
            COMBO_ALIASES[name.replace("bnb", "b&b")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "bandb")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "breadnbutter")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "bread&butter")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "breadandbutter")] = COMBO_ALIASES[name]
        if "overhead" in name:
            COMBO_ALIASES[name.replace("overhead", "oh")] = COMBO_ALIASES[name]

def getComboSequence(name):
    if len(COMBO_SEQUENCES) == 0:
        loadComboSequences()

    filterName = name.replace(" ", "").replace("-", "").lower()
    if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]

    if not filterName in COMBO_ALIASES or not COMBO_ALIASES[filterName] in COMBO_SEQUENCES:
        return ""
 
    return COMBO_SEQUENCES[COMBO_ALIASES[filterName]]