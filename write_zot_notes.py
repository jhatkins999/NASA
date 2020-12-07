import os
import random
import joblib

from produce_notes import *
from generate_predictions import *

from pyzotero import zotero

random.seed(params["RAND_SEED"])

# This file will output notes to Zotero


# This will output the notes and color code everything. Zotero uses html to output so changes colors, bold, underline etc.
# simply requires changing the html tags around the word you want
# output_note will change mentions of both the long name and the short name and returns a zotero note class
def output_note(sentences, mission, instrument, var, aliases, zot, tag_names, key):
    note_item = zot.item_template('note')
    note_text = []
    for d in sentences:
        sentence = d["sentence"]
        sentence = re.sub("-", " ", sentence)
        sentence = re.sub("/", " ", sentence)
        s = sentence.split(" ")
        if mission in aliases["mission_main"].keys() and aliases["mission_main"][mission] in sentence and aliases["mission_main"][mission] != "":
            mission_alias = aliases["mission_main"][mission].split(" ")
            s.insert(s.index(mission_alias[0]), "<font color = '#3336FF'>")  # Blue
            s.insert(s.index(mission_alias[-1]) + 1, "</font>")
        elif mission in sentence:
            s.insert(s.index(mission), "<font color =  '#3336FF'>")  # Blue
            s.insert(s.index(mission) + len(mission.split(" ")), "</font>")
        if instrument in aliases["instrument_main"].keys() and aliases["instrument_main"][instrument] in sentence:
            instrument_alias = aliases["instrument_main"][instrument].split(" ")
            s.insert(s.index(instrument_alias[0]), "<font color = '#FF3349'>")  # Red
            s.insert(s.index(instrument_alias[-1]) + 1, "</font>")
        elif instrument in sentence:
            s.insert(s.index(instrument), "<font color = '#FF3349'>")  # Red
            s.insert(s.index(instrument) + len(instrument.split(" ")), "</font>")
        if var in aliases["var_main"].keys() and aliases["var_main"][var] in sentence:
            var_alias = aliases["var_main"][var].split(" ")
            s.insert(s.index(var_alias[0]), "<font color = '#006400'>")  # Green
            s.insert(s.index(var_alias[-1]) + 1, "</font>")
        elif var in sentence:
            s.insert(s.index(var), "<font color = '#006400'>")  # Green
            s.insert(s.index(var) + len(var.split(" ")), "</font>")

        note_text += ["<p>"] + s + ["</p>"]

    note_text = " ".join(note_text)
    note_item["note"] = note_text

    for tag_name in tag_names:
        note_item["tags"].append({"tag": tag_name})

    return zot.create_items([note_item], key)


def output_note_exception(sentences, exception, aliases, tag_names, key):
    note_item = zot.item_template('note')
    note_text = []
    for d in sentences:
        sentence = d["sentence"]
        s = sentence.split(" ")
        if exception in aliases["exception_main"].keys() and aliases["exception_main"][exception] in sentence and aliases["exception_main"][exception] != "":
            exception_alias = aliases["exception_main"][exception].split(" ")
            s.insert(s.index(exception_alias[0]), "<font color = '#4B0082'>")  # Purple
            s.insert(s.index(exception_alias[-1]) + 1, "</font>")
        elif exception in sentence:
            s.insert(s.index(exception), "<font color =  '#4B0082'>")  # Purple
            s.insert(s.index(exception) + len(exception.split(" ")), "</font>")
        note_text += ["<p>"] + s + ["</p>"]

    note_text = " ".join(note_text)
    note_item["note"] = note_text

    for tag_name in tag_names:
        note_item["tags"].append({"tag": tag_name})

    return zot.create_items([note_item], key)


if __name__ == "__main__":

    library_id = params["GROUP_LIBRARY_KEY"]
    library_type = 'group'
    api_key = params['ZOTERO_API_KEY']
    # Connect to the Zotero API
    zot = zotero.Zotero(library_id, library_type, api_key)
    # Get the aura/mls collection
    collection = zot.collection(params['MLS_COLLECTION_ID'])

    # Check if we have recently loaded the files. If itemDict exists and you want to reload all the data fresh
    # set load_json = False in the config file. Note: it takes a few minutes to load all the data fresh
    if 'itemDict.json' in list(os.listdir("data/json")) and params['LOAD_JSON']:
        print("Loading values...")
        with open("data/json/itemDict.json", "r") as json_file:
            zot_items = json.load(json_file)
    else:
        print("Getting Zotero data...")
        zot_items = zot.everything(zot.collection_items(params["MLS_COLLECTION_ID"]))

        with open('data/json/itemDict.json', "w") as outfile:
            json.dump(zot_items, outfile, indent=4)
    print("Data loaded.")

    # Create an items dictionary so that time complexity for lookup is reduced
    items = {}
    for item in zot_items:
        items[item['key']] = item

    # Dump items so that it is easily referenced in the future
    with open("data/json/items.json", "w") as outfile:
        json.dump(items, outfile, indent=4)

    if params["TEST_CASE"]:
        print("Loading test set...")
        with open("data/json/test_set.json", "r") as json_file:
            test_items = json.load(json_file)

    with open("data/json/couples.json") as jsonfile:
        couples = json.load(jsonfile)

    with open("data/models/omi_model.joblib", "rb") as modelfile:
        model = joblib.load(modelfile)

    for file in os.listdir(params['PREPROC_LOC']):
        key = file.split(".")[0]
        if params["TEST_CASE"] and key not in test_items:
            continue
        if items[key]["data"]["itemType"] == "attachment":
            key = items[key]["data"]["parentItem"]
        print(key)


        fp = open(params['PREPROC_LOC'] + file, 'r')
        data, aliases = produce_notes(fp.read())

        ddict = defaultdict(int)
        for tag_pair in data.keys():
            if tag_pair[0] not in couples:
                continue
            if data[tag_pair][0]["exception"]:
                tag_list = ["ml_test6", data[tag_pair][0]["exception"]]
                val = output_note_exception(data[tag_pair], data[tag_pair][0]["exception"], aliases, tag_list, key)
            else:
                tag_list = ["ml_test6", "m/i:"+tag_pair[0], "var:"+tag_pair[1]]
                try:
                    val = output_note(data[tag_pair], data[tag_pair][0]["mission"], data[tag_pair][0]['instrument'],
                            data[tag_pair][0]['variable'], aliases, zot, tag_list, key)
                except Exception as e:
                    print("ERROR of type %s occured while trying to upload to %s" %(e, key))
                    val = False
            ddict[tag_pair] += len(data[tag_pair])
            if not val:
                print("Failed to upload note for article %s" %key)

        note_item = zot.item_template('note')
        note_item["note"] = predict(ddict, data, model)
        note_item["tags"].append({"tag" : "dataset_predictions"})
        note_item["tags"].append({"tag" : "ml_test6"})
        resp = zot.create_items([note_item], key)

        if not resp:
            print("Failed to upload prediction")

        # resp = zot.add_tags(items[key], 'ml_test5:jhatkins')
        if not resp:
            print(resp)
        exit()
