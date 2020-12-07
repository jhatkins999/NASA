from generate_predictions import predict
from produce_notes import *

from collections import defaultdict
import os
import time
import joblib
from tqdm import tqdm

from pyzotero import zotero
# this is one of several test files I have created to test different sets of papers
# this file has become increasingly messy over time and instead of fixing it I stopped using it and switched over the
# mls_tests file.


# Looks at the first few letters of the tag and returns the relevant tag.
def get_tag_from_pred(pred):
    pred = pred.lower()
    if 'ml' in pred:
        return "aura/mls"
    elif 'om' in pred:
        return "aura/omi"
    elif 'merra2' in pred:
        return "merra-2"
    elif 'merra' in pred:
        return "merra"
    elif "goz" in pred:
        return 'scisat-1/ace/ace-fts'
    elif "uar" in pred:
        if 'ml' in pred:
            return 'uars/mls'
        elif 'ha' in pred:
            return 'uars/haloe'
        elif 'cl' in pred:
            return 'uars/claes'
    else:
        return "Not Classified"

# Not relevant
def filter_test_results(test_result):
    filter = []
    for result in test_result:
        result = result.upper()
        if "\xa0" in result or "TOMS" in result:
            continue
        elif"SBUV" in result or "MA" in result or "ML2" in result or "OM" in result or "UAR" in result or "GOZ" in result or 'M2' in result:
            filter.append(result)
        else:
            print("Non Standard:",result)
    return filter

# Pretty print the results
def print_results(results, name):
    print("\t%s Successes Predict Dataset Accuracy" %name)
    for key in results.keys():
        if results[key]["Datasets"] == 0:
            acc = "N/A"
        else:
            acc = results[key]["Successes"] / results[key]["Datasets"]
        print("\t" + key + "\t" + str(results[key]["Successes"]) + "\t" + \
              str(results[key]["Predictions"]) + "\t" + \
              str(results[key]["Datasets"]) + "\t" + str(acc))


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

    test_items = defaultdict(list)
    test_results = defaultdict(list)
    josh6 = []

    for item in zot_items:
        if item["data"]["itemType"] == "note":
            for tag in item["data"]["tags"]:
                if "category:application" in tag["tag"]:
                    if item['data']['parentItem'] + ".pdf.txt" in os.listdir(params['PREPROC_LOC']):
                        key = item["data"]["parentItem"]
                        test_items[key].append(items[key])
                        for result in item["data"]["note"].split("\n"):
                            tag = re.sub("<[^>]+>", "", result)
                            test_results[key].append(tag)
        elif item["data"]["itemType"] == "journalArticle":
            if [i["tag"] for i in item["data"]["tags"] if i["tag"] == "reviewed:joshuathedford6"]:
                josh6.append(item["data"]["key"])
    print("%s josh6 articles found" % len(josh6))
    total, successes, datasets = 0, 0, 0
    num = 0
    start_time = time.time()
    loop_time = time.time()
    with open("data/json/couples.json") as jsonfile:
        couples = json.load(jsonfile)
    with open("data/json/skip.json") as jsonfile:
        skip = json.load(jsonfile)
    # with open("data/json/scopus.json", "w") as jsonfile:
    #     json.dump(scopus, jsonfile, indent=4)
    with open("data/models/omi_model.joblib", "rb") as modelfile:
        model = joblib.load(modelfile)

    tag_breakdown = {}
    scopus_data = {}
    non_scopus_data = {}
    scopus = []
    josh62 = []

    for file in os.listdir(params['PREPROC_LOC']): # Add back tqdm
        key = file.split(".")[0]
        try:
            if items[key]["data"]["itemType"] == "attachment":
                key = items[key]["data"]["parentItem"]
        except KeyError:
            continue
        if key not in josh6:
            continue
        print(key)
        josh62.append(key)

        if (num % 10 == 0 and num != 0):
            print("%s tests completed.\n\tSuccesses: %s\n\tTotal: %s\n\tDatasets: %s\n\tAccuracy %s"
                  % (num, successes, total, datasets, successes + total))
            # print_results(tag_breakdown, "Overall")
            # print_results(scopus_data, "Scopus")
            # print_results(non_scopus_data, "Non-Scopus")

            print("\tIt took %s seconds to complete the last 10 and has taken %s time total"
                  % (time.time() - loop_time, time.time() - start_time))
            loop_time = time.time()
        num += 1

        filtered = filter_test_results(test_results[key])
        for dataset in filtered:
            tag = get_tag_from_pred(dataset)
            if tag in tag_breakdown:
                tag_breakdown[tag]["Datasets"] += 1
                if key in scopus:
                    if tag in scopus_data:
                        scopus_data[tag]["Datasets"] += 1
                    else:
                        scopus_data[tag] = {"Total": 1,
                                            "Successes": 0,
                                            "Predictions": 0,
                                            "Datasets": 1}
                else:
                    if tag in non_scopus_data:
                        non_scopus_data[tag]["Datasets"] += 1
                    else:
                        non_scopus_data[tag] = {"Total": 1,
                                                "Successes": 0,
                                                "Predictions": 0,
                                                "Datasets": 1}
            else:
                tag_breakdown[tag] = {"Total" : 1,
                                      "Successes" : 0,
                                      "Predictions" : 0,
                                      "Datasets" : 1}
                if key in scopus:
                    scopus_data[tag] = {"Total": 1,
                                        "Successes": 0,
                                        "Predictions": 0,
                                        "Datasets": 1}
                else:
                    non_scopus_data[tag] = {"Total": 1,
                                            "Successes": 0,
                                            "Predictions": 0,
                                            "Datasets": 1}

        total += len(filtered)

        fp = open(params['PREPROC_LOC'] + file, 'r')
        data, aliases = produce_notes(fp.read())
        ddict = defaultdict(int)

        predictions = {}
        for tag_pair in data.keys():
            if tag_pair[0] in skip or tag_pair[0] not in couples:
                continue

            if tag_pair[0] in tag_breakdown:
                tag_breakdown[tag_pair[0]]["Total"] += 1
                if key in scopus:
                    scopus_data[tag_pair[0]]["Total"] += 1
                else:
                    non_scopus_data[tag_pair[0]]["Total"] += 1
            else:
                tag_breakdown[tag_pair[0]] = {"Total" : 1,
                                              "Successes" : 0,
                                              "Predictions" : 0,
                                              "Datasets" : 0}
                if key in scopus:
                    scopus_data[tag_pair[0]] = {"Total": 1,
                                                "Successes": 0,
                                                "Predictions": 0,
                                                "Datasets": 0}
                else:
                    non_scopus_data[tag_pair[0]] = {"Total": 1,
                                                    "Successes": 0,
                                                    "Predictions": 0,
                                                    "Datasets": 0}
            ddict[tag_pair] += len(data[tag_pair])
        prediction = predict(ddict, data, model)

        correct = []
        used = []
        count = 0

        for pred in prediction.split("<p>")[2:]:
            print(pred)
            dataset = re.sub("<[^>]+>", "", pred).split(" ")[0]
            if dataset in used:
                continue
            used.append(dataset)

            datasets += 1

            tag = get_tag_from_pred(pred)
            if tag == "Not Classified":
                print("NOT CLASSIFED", pred)
            if tag in tag_breakdown:
                tag_breakdown[tag]["Predictions"] += 1
                if key in scopus:
                    scopus_data[tag]["Predictions"] += 1
                else:
                    non_scopus_data[tag]["Predictions"] += 1
            else:
                tag_breakdown[tag] = {"Total" : 1,
                                      "Successes" : 0,
                                      "Predictions" : 1,
                                      "Datasets" : 0}
                if key in scopus:
                    scopus_data[tag] = {"Total": 1,
                                        "Successes": 0,
                                        "Predictions": 1,
                                        "Datasets": 0}
                else:
                    non_scopus_data[tag] = {"Total": 1,
                                            "Successes": 0,
                                            "Predictions": 1,
                                            "Datasets": 0}

            if dataset in filtered and dataset not in correct:
                count += 1
                tag_breakdown[tag]["Successes"] += 1
                if key in scopus:
                    scopus_data[tag]["Successes"] += 1
                else:
                    non_scopus_data[tag]["Successes"] += 1
                successes += 1
                correct.append(dataset)
        if len(filtered) == 0:
            acc = "N/A"
        else:
            acc = count / len(filtered)
        predictions[key] = {"Predictions"  : len(prediction.split("\n")),
                            "Successes"    : count,
                            "Datasets"     : len(filtered),
                            "Accuracy"     : acc
                            }
        missed = list(set(filtered) - set(correct))

        if missed:
            print("Missed Datasets for %s" %key)
            print("\t",missed)

    print(total, successes, datasets)
    print(tag_breakdown)