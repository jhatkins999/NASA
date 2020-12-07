import operator
from sklearn.feature_extraction.text import CountVectorizer
# This file will need the most editing in the future. It might be wise to just take the easy code and start over.
# This predicts the code from MLS/Aura and has filler code for the ML algorithm that will be used to classify Aura/OMI.
# This will output text that can be outputted directly to Zotero it will be a list of potential datasets and the number
# of mentions that they contain


# predict takes a dictionary containing a list of all references and the data dictionary which contains all the references
# and potential tags, it can also take an ML model used to analyze Omi. If it is not a specified dataset for
# example then the output should be of the form dataset_short_name/variable   count.
def predict(ddict, data, omi_model=None):
    text = "<p>DATASET FREQUENCY</p>"
    ordered = sorted(ddict.items(), key=operator.itemgetter(1), reverse=True)
    for item in ordered:
        key, value = item[0], item[1]
        if data[key][0]["exception"]:
            text += "<p>"+key[0]+" "+str(value)+"</p>"
        elif key[0] == "aura/mls":
            # Quick stop to not let the word no skew the results. In the future this should be taken care of by a POS
            # tagger
            if key[1].lower() == "no":
                continue
            prediction = "ML2" + key[1].upper()
            text += "<p>"+prediction + " " + str(value)+"</p>"
        elif key[0] == "aura/omi":
            try:
                for reference in data[key]:
                    sentence = reference["sentence"]
                    text += "<p>" + omi_model.predict([sentence])[0] + " " + str(value) + "</p>"
            except Exception as e:
                print("Model failed: %s" %e)
        # UARS should be another simple dataset to label, however there are only like 10 instances within aura/MLS
        elif 'uars' in key[0]:
            if 'haloe' in key[0]:
                text += "<p>" + "UARHA2FN" + " " + str(value) + "</p>"
                text += "<p>" + "UARHA3AT" + " " + str(value) + "</p>"
            elif 'mls' in key[0]:
                text += "<p>" + "UARML3AT" + " " + str(value) + "</p>"
                text += "<p>" + "UARML3AL" + " " + str(value) + "</p>"
            elif 'claes' in key[0]:
                text += "<p>" + "UARCL3AT" + " " + str(value) + "</p>"
                text += "<p>" + "UARCL3AL" + " " + str(value) + "</p>"
        else:
            prediction = key[0]+"/"+key[1]
            text += "<p>"+prediction + " " + str(value)+"</p>"

    return text