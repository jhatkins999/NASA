from config import params

from utils import *
import shutil
from subprocess import Popen
from tqdm import tqdm
import os
import json
# This collects the pds from the pdfs folder and converts them to txt files. This is a long process and takes
# about 2 minutes for each pdf to be converted.

if __name__ == "__main__":
    print("There are %s pdfs in the pdf folder" %len(os.listdir(params["PDF_LOC"])))
    for folder in os.listdir(params['ZOTERO_LOC']):
        if folder[0] == ".":
            continue
        for file in os.listdir(params['ZOTERO_LOC']+"/"+folder):
            if file.split(".")[-1] == "pdf":
                if folder+".pdf" not in os.listdir(params["PDF_LOC"]):
                    shutil.copy(params['ZOTERO_LOC']+"/"+folder+"/"+file, params["PDF_LOC"]+"/"+folder+".pdf")
    print("After new pdfs there are now %s pdfs in the pdf folder" %len(os.listdir(params["PDF_LOC"])))
    sub_n = params["SUBPROC"]

    print("CONVERTING PDF TO TXT")

    pdf_files = os.listdir(params["PDF_LOC"])
    converts = []
    pdfs = []
    test = []
    with open("data/json/scopus.json") as jsonfile:
        scopus = json.load(jsonfile)
    count = 0
    for file in pdf_files:
        input_file = file
        output_file = "data/text/" + input_file.split("/")[-1] + ".txt"
        if output_file.split("/")[-1] in os.listdir(params["TEXT_LOC"]):
            test.append(input_file)
            continue
        else:
            pdfs.append(input_file)

    commands = []
    for i in range(len(pdfs)):
        input_file = params["PDF_LOC"]+"/"+pdfs[i]
        output_file = "data/text/" + input_file.split("/")[-1] + ".txt"

        if i % sub_n == 0:
            commands = []
            command = ["pdf2txt.py", "-o", output_file, input_file]
            commands.append(command)
        elif i % sub_n == sub_n - 1:
            command = ["pdf2txt.py", "-o", output_file, input_file]
            commands.append(command)
            converts.append(commands)
        elif i == len(pdfs) - 1:
            command = ["pdf2txt.py", "-o", output_file, input_file]
            commands.append(command)
            converts.append(commands)
        else:
            command = ["pdf2txt.py", "-o", output_file, input_file]
            commands.append(command)

    print("Running %s processes at once to convert pdfs" % sub_n)
    for commands in tqdm(converts, ascii=True, desc='pdf->txt'):
        try:
            procs = [Popen(i) for i in commands]
            for p in procs:
                p.wait()
        except Exception as e:
            print(e)