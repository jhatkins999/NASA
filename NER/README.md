# NER Notes
This readme is from the code I was running in the summer. The code was not particularly accurate and had
terrible recall. Fixing this requires changing the input to input individual sentences each of which
contains the possible mentions and then creating the linking model and checking the accuracy. 
This might require a change in the NER model and the input. For example, it might be easier to run 
the ner rcc file to create the conll file and then input our new conll file into the different ner model.
https://stanfordnlp.github.io/CoreNLP/ner.html That is the link to the stanford NLP ner model which
is written in Java but has an nltk python wrapper and can be imported with 
from nltk.tag import StanfordNERTagger
NLTK is installed as part of the yaml file. This file takes a model and a jar file, the classes of the
model can be changed which allows us to import our model with an extra class for datasets. It takes a
tar gz file which can be generated with the steps outlined in the README. The model from last summer
can be found in NER/project/model/model.tar.gz

# Summer README
To run this project, you need to be running a linux based system and have anaconda downloaded

To create the environment run the command:
    conda env create -f environment.yml
After the environment is created the spacy model needs to be installed manually:
    python -m spacy download en_core_web_sm 
Then export the pythonpath to make sure you can run your modules:
    PYTHONPATH=PathToFolder
    export PYTHONPATH
    
To run the preprocessing code
    1. cd preprocessing
    2. python preprocessing.py --process_citations 1 
           --process_publications 1 --pdf2txt 1 --split_paragraphs 1 --create_test 1
    Note: It takes around 2 hours to process all the PDF's. Edit the subproc param to use more threads
    to find the number of threads to run on run $ sysctl hw.logicalcpu
    
To run the NerModel Code:
    1. cp data/json/publications_train.json ../NerModel/data/train
       cp data/json/publications_test.json ../NerModel/data/test
       cp data/json/publications_dev.json ../NerModel/data/dev
       cp data/json/data_sets.json ../NerModel/data
    2. python project/get_docs.py
    3. python project/to_conll.py --data_folder_path data
    4. python project/ner_retraining/create_splits.py
    5. rm -r project/model/* 
    6. allennlp train project/ner_model -s project/model --include-package project/ner_rcc
    7. python project/to_conll_test.py # Might not be necessary
    8. python project/ner_retraining/generate_ner_output.py --conll_path data/test/ner-conll --output_path data/output/ner_output --model_path project/model
    

    
