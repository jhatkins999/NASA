import csv
import re
import json
from collections import defaultdict
import itertools

from config import params

# This code will produce the notes that are entered into Zotero. Each note containes an exact text match with a
# mission/instrument and variable pair or with a match with one of the exceptions. The exceptions include all datasets
# labeled with the Microwave limb sounder and each of the data models.


# Extracts the variables from the mission, instrument, and variable csvs. This will extract both the short names and
# the long names. It will output a list of all missions, variables and instruments and all the potential pairs
# The aliases dictionaries contain mapping from short name to long name and the main dictionaries contain a mapping from
# long name to short name
def get_variables(var_path, mission_path, instrument_path, exception_path):
    var_aliases = {}
    var_main = {}
    mission_aliases = {}
    mission_main = {}
    instrument_aliases = {}
    instrument_main = {}
    exceptions_main = {}
    exceptions_aliases = {}

    exceptions = []
    with open(exception_path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            exceptions.append(row[0].lower())
            if row[1]:
                exceptions.append(row[1].lower())
                exceptions_aliases[row[1].lower()] = row[0].lower()
            exceptions_main[row[0].lower()] = row[1].lower()

    variables = []
    with open(var_path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            variables.append(row[0].lower())
            if row[1]:
                variables.append(row[1].lower())
                var_aliases[row[1].lower()] = row[0].lower()
            var_main[row[0].lower()] = row[1].lower()

    instruments = []
    with open(instrument_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in reader:
            count += 1
            if row[5]:
                instrument_aliases[row[5].lower()] = row[4].lower()
            instrument_main[row[4].lower()] = row[5].lower()
            for i in range(4, 6):
                if row[i]:  # and not re.search(r"(/|\()", row[i]):
                    instruments.append(row[i].lower())

    missions = []
    with open(mission_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[3]:
                mission_aliases[row[3].lower()] = row[2].lower()
            mission_main[row[2].lower()] = row[3].lower()
            for i in range(2, 4):
                if row[i]:  # and not re.search(r"(/|\()", row[i]):
                    missions.append(row[i].lower())
    missions.append("mls")
    missions.append("microwave limb sounder")

    aliases = {
        "mission_aliases" : mission_aliases,
        "mission_main" : mission_main,
        "instrument_aliases" : instrument_aliases,
        "instrument_main" : instrument_main,
        "var_aliases" : var_aliases,
        "var_main" : var_main,
        "exception_main" : exceptions_main,
        "exception_aliases" : exceptions_aliases
    }
    with open("data/json/aliases.json", "w") as jsonfile:
        json.dump(aliases, jsonfile, indent=4)
    jsonfile.close()

    return missions, instruments, variables, exceptions, aliases

# This will output the potential tags. It simply takes the possible permutations of the missions, instruments and variables
# and outputs all the possible permutations of each that occur. Note again that MLS implies the aura satellite
def get_tags(mission, instrument, variable, aliases):
    tags = []
    completed = []
    for perm in itertools.product(*[mission, instrument, variable]):
        if perm in completed:
            continue
        else:
            completed.append(perm)
        if perm[0] in aliases["mission_aliases"]:
            mis = aliases["mission_aliases"][perm[0]].lower()
        elif perm[0] in aliases["mission_main"]:
            mis = perm[0]
        else:
            mis = perm[0]
        if perm[1] in aliases["instrument_aliases"]:
            ins = aliases["instrument_aliases"][perm[1]]
        elif perm[1] in aliases["instrument_main"]:
            ins = perm[1]
        else:
            ins = perm[1]
        if perm[2] in aliases["var_aliases"]:
            var = aliases["var_aliases"][perm[2]]
        elif perm[2] in aliases["var_main"]:
            var = perm[2]
        else:
            var = perm[2]
        if mis == "mls" or mis == "microwave limb sounder":
            mis = "aura"
        if (mis+"/"+ins, var) not in tags:
            tags.append((mis+"/"+ins, var))
    return tags


def is_ordered_subset(subset, sentence):
    sub = subset.split(" ")
    lst = sentence.split(" ")
    ln = len(sub)
    for i in range(len(lst) - ln + 1):
        if all(sub[j] == lst[i+j] for j in range(ln)):
            return True
    return False


# This function takes the text of a preprocessed txt document and outputs the notes. Each note contains all
# the notes for each (mission/instrument, variable) tuple. It also passes through the aliases used in this file
# The output format is a dictionary with key = (mission/instrument, variable) and value = list of sentences with matches
def produce_notes(text):
    var_path = params['VARIABLES_CSV']
    mission_path = params['MISSIONS_CSV']
    instrument_path = params["INSTRUMENTS_CSV"]
    exception_path = params["EXCEPTION_CSV"]

    missions, instruments, variables, exceptions, aliases = get_variables(
        var_path, mission_path, instrument_path, exception_path)

    text = re.sub("[\(\[].*?[\)\]]", "", text)
    text = re.sub("\n", " ", text)
    text = re.sub("- ", "", text)
    text = re.sub("/", " ", text)

    data = defaultdict(list)

    for s in text.split("."):
        mission = []
        instrument = []
        var = []
        exception = []

        for e in exceptions:
            if is_ordered_subset(e, s.lower()):
                exception.append(e)

        for m in missions:
            if is_ordered_subset(m, s.lower()):
                mission.append(m)
        if not mission and not exception:
            continue
        for i in instruments:
            if is_ordered_subset(i, s.lower()):
                instrument.append(i)
        if not instrument and not exception:
            continue
        for v in variables:
            if is_ordered_subset(v, s.lower()):
                var.append(v)
        if not var and not exception:
            continue

        else:
            for tag in get_tags(mission, instrument, var, aliases):
                data[tag].append({
                    "sentence" : s,
                    "mission" : tag[0].split("/")[0],
                    "instrument" : tag[0].split("/")[1],
                    "variable" : tag[1],
                    "exception" : False
                })

            for e in exception:
                if e in aliases["exception_aliases"]:
                    e = aliases["exception_aliases"][e]
                data[(e, "none")].append({
                    "sentence" : s,
                    "mission" : False,
                    "instrument": False,
                    "variable": False,
                    "exception" : e
                })

    return data, aliases

