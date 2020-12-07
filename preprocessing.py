from config import params

import re # need to take out /n from text
import os
from unidecode import unidecode

# This will split the document and only take the relevant paragraphs. All paragraphs being taken creates alot of noise
# as they may reference results in more glancing ways and not provide enough information. Additionally, many of the
# references section will match keywords and create a lot of false positives.


# The splitting splits all paragraphs deliniated by /n/n and then checks to see if the section is either an acceptable
# section which is determined by matching to the paragraph_labels list in the config file. Additionally, if a paragraph
# contains a doi the paragraph is considered to be a reference section and skipped. Note: some files do not have any
# matching paragraphs. This probably needs to be fixed by running the ones that don't work through different preprocessing
# or maybe just looking at some of these papers and changing the possible labels in the config file.
def split_doc_paragraphs(src=params["TEXT_LOC"], dest=params["PREPROC_LOC"],
                         remove_stopwords=params["REMOVE_STOPWORDS"], labels=params['PARAGRAPH_LABELS']):

    max_len = len(max(labels, key=len))

    for doc in os.listdir(src):
        fp = open(src + doc)
        txt = fp.read()
        txt = unidecode(txt)
        paragraphs = txt.split("\n\n")
        outtxt = ""
        ind = -1
        if "References" in paragraphs and False:
            ind = paragraphs.index("References")
        else:
            for p in range(len(paragraphs)):
                if "doi" in paragraphs[p].lower() and p > 5:
                    ind = p
                    break
        paragraphs = paragraphs[:ind]
        for i in range(len(paragraphs)):
            para = paragraphs[i].lower()
            if any(label.lower() in para for label in labels):
                if len(para) > 2 * max_len or i == len(paragraphs) - 1:
                    outtxt += para
                else:
                    outtxt += paragraphs[i + 1]
        with open(dest + doc, "w") as out:
            out.write(outtxt)


if __name__ == "__main__":
    split_doc_paragraphs()
