from config import  params
from produce_notes import produce_notes

import json
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import os

# Load the relevant reviewed paper keys
with open(params['JSON_LOC']+"reviewed.json") as jsonfile:
    reviewed = json.load(jsonfile)
# Load the notes from the reviewed files
with open("data/json/reviewed_notes.json") as jsonfile:
    notes = json.load(jsonfile)
# load all of the couple pairs
with open("data/json/couples.json") as jsonfile:
    couples = json.load(jsonfile)
# Load the items file
with open("data/json/items.json") as jsonfile:
    items = json.load(jsonfile)

# Pass the model and jar file to the NER tagger
model = params['MODEL_LOC']
jar = params['JAR_LOC']
st = StanfordNERTagger(model, jar, encoding='utf-8')

mentions = []
for key in reviewed:
    # Skip all files we don't have notes for
    if key not in notes:
        continue

    # Get the correct filename from the key, this may become obselete if you change the naming system
    file = key + ".pdf.txt"

    if file not in os.listdir(params["PREPROC_LOC"]):
        key = items[key]['data']['parentItem']
        file = key + ".pdf.txt"
        if file not in os.listdir(params["PREPROC_LOC"]):
            print("FILE %s not found" % file)

    with open(params["PREPROC_LOC"] + file) as fp:
        txt = fp.read()
    data, _ = produce_notes(txt)

    for tag_pair in data:
        if tag_pair[0] not in couples:
            continue
        input[tag_pair] += len(data[tag_pair])

    for key in data:
        for sentence in data[key]:
            mentions.append(sentence)
predictions = []
for mention in mentions:
    words = word_tokenize(sentence)
    predictions.append(st.tag(words))

# Print out the predictions
print(predictions[0])

