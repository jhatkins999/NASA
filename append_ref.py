# NOTES:
# NOTE 1:
    # There is a spacing problem some of the words don't have spaces between them
    # I think this is a new line problem
# NOTE 2:
    # This code does not include level as most papers don't include level
# Note 3:
    # Manually added in [microwave, limb, sounder] because right now the program searches one word at a time
    # Trying to seperate all instruments by word fails miserably -- too many matches

import os
import csv
import re
import time
from collections import defaultdict
from nltk.corpus import stopwords

from config import params


def get_variables(var_path, mission_path, instrument_path):
    variables = []
    # with open(var_path, newline='') as csvfile:
    #     reader = csv.reader(csvfile, delimiter=',')
    #     for row in reader:
    #         if row[4] and not re.search(r"(/|\()", row[4]):
    #             variables.append(row[4].lower())
    # variables = sorted(set(variables), key=len, reverse=True)
    with open(var_path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            variables.append(row[0].lower())

    instruments = []
    with open(instrument_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            for i in range(4, 6, 1):
                if row[i]:  # and not re.search(r"(/|\()", row[i]):
                    instruments.append(row[i].lower())
    instruments = sorted(set(instruments), key=len, reverse=True)

    missions = []
    with open(mission_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            for i in range(2, 4, 1):
                if row[i]:  # and not re.search(r"(/|\()", row[i]):
                    missions.append(row[i].lower())
    missions = sorted(set(missions), key=len, reverse=True)

    return missions, instruments, variables


def get_matches(words, missions, instruments, variables):
    stop_words = stopwords.words("english")
    # Maybe just loop and use re
    instruments += ["microwave", "limb", "sounder"] # Fix in general fine for now, in the future use re sub on all transforms
    instrument = set(instruments).intersection(set(words)) - set(stop_words)
    mission = set(missions).intersection(set(words)) - set(stop_words)
    var = set(variables).intersection(set(words)) - set(stop_words)
    # if bool(instrument) + bool(mission) + bool(var) > 2:
    #     print("INSTRUMENT:", instrument)
    #     print("MISSION:", mission)
    #     print("VARIABLE:", var)
    #     print("WORDS:", words)
    return bool(mission), bool(instrument), bool(var)


if __name__ == "__main__": # Add function call instead of main
    start_time = time.time()
    text_path = params['PREPROC_LOC']
    var_path = params['VARIABLES_CSV'] # This one doesnt work create your own
    mission_path = params['MISSIONS_CSV']
    instrument_path = params["INSTRUMENTS_CSV"]

    missions, instruments, variables = get_variables(var_path, mission_path, instrument_path)
    print(instruments[:20])
    exit()
    files = os.listdir(text_path)

    append_ref = {}
    zot_notes = defaultdict(list)
    n = params["NUM_SENTENCES"]

    for file in files:

        loop_time = time.time()
        fp = open(text_path + file, 'r')
        text = fp.read()
        text = re.sub("[\(\[].*?[\)\]]", "", text)
        text = re.sub("\n", " ", text)

        sentences = text.split(".")
        ref = []

        switches = []
        for i in range(len(sentences)):
            switches.append([0,0,0])


        for s, switch in zip(sentences, switches):
            words = s.split(" ")
            words = list(map(lambda x : x.lower(), words))
            m, i, v = get_matches(words, missions, instruments, variables)
            switch[0] += m
            switch[1] += i
            switch[2] += v
            if switch == [1,1,1]:
                zot_notes[file.split(".")[0]].append(s)


        n_switches = []
        n_sent = []
        for i in range(len(switches) - n):
            switch_group = switches[i:i+n]
            vec = [0,0,0]
            for switch in switch_group:
                vec[0] += switch[0]
                vec[1] += switch[1]
                vec[2] += switch[2]
            n_switches.append(vec)
            n_sent.append(".".join(sentences[i:i+n]))

        for i in range(len(n_switches)):
            if all(n_switches[i]):
                ref.append(n_sent[i])
        append_ref[file.split(".")[0]] = (len(ref), ref)
        print("There were %s references found in file %s" %(len(ref), file))
        print("This loop took %s seconds to run" %(time.time() - loop_time))


total = sum([x[0] for x in append_ref.values()])
average = total / len(files)
print("TOTAL:", total)
print("AVERAGE:", average)
print("The program took %s seconds to run" %(time.time() - start_time))

import json
with open("data/json/references.json", "w") as jsonfile:
    json.dump(append_ref, jsonfile, indent=4)

with open("data/json/zot_notes.json", "w") as jsonfile:
    json.dump(zot_notes, jsonfile, indent=4)