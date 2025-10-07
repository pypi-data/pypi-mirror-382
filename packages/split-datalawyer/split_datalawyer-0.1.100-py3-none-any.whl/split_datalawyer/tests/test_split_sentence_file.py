import os
from split_datalawyer.sentences.sentence_split import SentenceSplit
from split_datalawyer.modules import *

massive_avaliation = False
# massive_avaliation = True

SPLIT_SEMICOLON = massive_avaliation

files_content = []
files_base = []

local_path = os.path.dirname(__file__)

if massive_avaliation:
    local_path = os.path.join(local_path, "massive_avaliation")

examples_dir = os.path.join(local_path, "examples")
base_splitted_dir = os.path.join(local_path, "base_splitted")
new_base_dir = os.path.join(local_path, "new_base")
files = os.listdir(examples_dir)

sentence_split = SentenceSplit(debug_log=True,
                               modules=[ForceDropPageNumberLinesModule(), ReplaceModule()])

for file in files:
    if file == 'example17.txt':
        with open(os.path.join(examples_dir, file), "r", encoding="utf8") as fs:
            content = fs.read()

        base_file_name = file.replace(".txt", ".base")
        base_file_path = os.path.join(base_splitted_dir, base_file_name)

        if os.path.exists(base_file_path):
            with open(base_file_path, "r", encoding="utf8") as fs:
                target_content = fs.readlines()
        else:
            files_base.append((file, ""))
            target_content = []

        sentences = sentence_split.get_sentences(content, remove_duplicated=False,
                                                 remove_stop_phrases=True,
                                                 concat_inverted_phrases=False,
                                                 split_by_semicolon=False)
        print(sentences)
