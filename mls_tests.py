from generate_predictions import predict
from produce_notes import *

from collections import defaultdict
import os
import joblib

from pyzotero import zotero
# Clean test file used to find the accuracy of all the papers with the reviewed:igerisimov tag
# this is the latest version of the tests I was doing. I reccomend to create your own test file though to suit your needs
# the test code is commented so you should be able to take any functions you think are useful.


if __name__ == "__main__":
    library_id = params["GROUP_LIBRARY_KEY"]
    library_type = 'group'
    api_key = params['ZOTERO_API_KEY']

    zot = zotero.Zotero(library_id, library_type, api_key)

    if 'itemDict.json' in list(os.listdir("data/json")) and params['LOAD_JSON']:
        print("Loading values...")
        with open("data/json/itemDict.json", "r") as json_file:
            zot_items = json.load(json_file)
    else:
        print("Getting Zotero data...")
        zot_items = zot.everything(zot.collection_items(params["MLS_COLLECTION_ID"]))
        zot_items += zot.everything(zot.collection_items(params["SCOPUS_COLLECTION_ID"]))
        with open('data/json/itemDict.json', "w") as outfile:
            json.dump(zot_items, outfile, indent=4)
    print("Data loaded.")
    items = {}
    for item in zot_items:
        items[item['key']] = item

    with open("data/json/items.json", "w") as outfile:
        json.dump(items, outfile, indent=4)

    with open("data/json/couples.json") as jsonfile:
        couples = json.load(jsonfile)

    with open("data/models/omi_model.joblib", "rb") as modelfile:
        model = joblib.load(modelfile)

    with open("data/json/reviewed_notes.json") as jsonfile:
        notes = json.load(jsonfile)

    with open("data/json/correctly_reviewed.json") as jsonfile:
        reviewed = json.load(jsonfile)

    count = 0
    total, skipped, complete = 0, 0, 0
    correct_predictions, relevent_predictions, attempted_predictions = 0, 0, 0
    # Reviewed is a list of all articles that contain the reviewed:igerisimov tag
    for key in reviewed:
        print(key)
        if key not in notes:
            continue
        else:
            count += 1

        # Get the correct filename from the key, this may become obselete if you change the naming system
        file = key+".pdf.txt"
        if file not in os.listdir(params["PREPROC_LOC"]):
            key = items[key]['data']['parentItem']
            file = key + ".pdf.txt"
            if file not in os.listdir(params["PREPROC_LOC"]):
                print("FILE %s not found" %file)

        # notes.json contains all the possible notes text indexed by the key Zotero gave it.
        file_notes = notes[key]
        correct_datasets = []
        for note in file_notes:
            for tag in note['data']['tags']:
                # All the correct labels are contained within notes that have the category application tag
                if "category:application" in tag['tag']:
                    for i in note['data']['note'].split("<p>"):
                        # take only the mls datasets for this test
                        if "ML2" not in i:
                            continue
                        i = re.sub("\n", "", i)
                        # This is the list of the ground truth datasets contained in the paper
                        correct_datasets.append(re.sub("<[^>]+>", "", i).split(" ")[0])

        with open(params["PREPROC_LOC"]+file) as fp:
            txt = fp.read()
        # Produce the notes by entering the preprocessed paper text
        data, aliases = produce_notes(txt)
        input = defaultdict(int)
        # Check to only predict that datasets that have valid couples. Valid couples are contaiened within couples.json
        # which is one of the only json files I uploaded
        for tag_pair in data:
            if tag_pair[0] not in couples:
                continue
            input[tag_pair] += len(data[tag_pair])
        # Predict the relevant datasets
        prediction = predict(input, data, model)
        # print(correct_datasets)
        total += 1
        c,a  = 0, 0

        # This loop will split the predictions and then determine the number of relevant prediction and the number
        # of matches.
        for pred in prediction.split("<p>")[2:]:
            if "ML2" not in pred:
                continue
            d = re.sub("<[^>]+>", "", pred).split(" ")
            pred_dataset, n = d[0], d[1]
            attempted_predictions += 1
            a += 1
            # print(pred_dataset, pred_dataset in correct_datasets)
            if pred_dataset in correct_datasets:
                correct_predictions += 1
                c += 1
        relevent_predictions += len(correct_datasets)
        complete += int(len(correct_datasets) == c == a)
        # print(correct_predictions, relevent_predictions, complete)
    print("FINAL\n\n")
    print(correct_predictions, relevent_predictions, attempted_predictions)
    precision, recall = correct_predictions / attempted_predictions, correct_predictions / relevent_predictions
    print("PRECISION:", precision)
    print("RECALL:", recall)
    print("F1:", 2 * precision * recall / (precision + recall))
    print(skipped, total, complete, total - skipped)