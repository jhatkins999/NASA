import os
import numpy as np
from produce_notes import *
from pyzotero import zotero
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
import joblib
# This file is just an easy test file to do some basics ml tests on the data. It tests out three different
# sklearn models, a naive bayes, a support vector machine, and an adaboost. Initial tests don't show much difference
# and the models are not particularly accurate, naive bayes performed best with about a 40% accuracy.


# Get data pulls the data from zotero and then takes only notes that have been tagged with reviewed:igerasimov
# papers that we consider to have been labeled with the ground truth data.
def get_data():
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
    items = {item['key'] : item for item in zot_items}
    notes = defaultdict(list)
    for item in zot_items:
        if item['data']['itemType'] == 'note':
            notes[item['data']['parentItem']].append(item)
    output = defaultdict(list)
    for file in os.listdir(params["PREPROC_LOC"]):
        key = file.split(".")[0]
        if key not in items or {"tag" : "reviewed:igerasim"} not in items[key]["data"]["tags"]:
            continue
        for note in notes[key]:
            tags = note['data']['tags']
            if any(["dataset:om" in tag["tag"].lower() for tag in tags]):
                for tag in note['data']['tags']:
                    if "dataset:om" not in tag["tag"].lower():
                        continue
                    for mention in note['data']['note'].split("</p>"):
                        output[tag["tag"].split(":")[-1]].append(re.sub("<[^>]+>", "", mention))

    return output


data = get_data()
X, y = [], []
for key in data:
    for mention in data[key]:
        if mention:
            X.append(mention)
            y.append(key)
trainX, testX, trainy, testy = train_test_split(X, y, test_size=.4)



naive = Pipeline([
    ('vect', CountVectorizer()),
    ('clf', MultinomialNB())
])
naive.fit(trainX, trainy)
predicted = naive.predict(testX)
print(len(predicted), len(testy))
print(np.mean([int(predicted[i]==testy[i]) for i in range(len(predicted))]))


svm = Pipeline([
    ('vect', CountVectorizer()),
    ('clf', SVC())
])

svm.fit(trainX, trainy)
predicted = svm.predict(testX)
print(np.mean([int(predicted[i]==testy[i]) for i in range(len(predicted))]))

adaboost = Pipeline([
    ('vect', CountVectorizer()),
    ('clf', AdaBoostClassifier(n_estimators=100))
])
adaboost.fit(trainX, trainy)
predicted = adaboost.predict(testX)
print(np.mean([int(predicted[i]==testy[i]) for i in range(len(predicted))]))

with open("data/models/omi_model.joblib", "wb") as pkl:
    joblib.dump(naive, pkl, compress=1)
