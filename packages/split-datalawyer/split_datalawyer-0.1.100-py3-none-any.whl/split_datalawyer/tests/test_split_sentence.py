import os
from typing import List
from pathlib import Path
from split_datalawyer.sentences.sentence_split import SentenceSplit
from split_datalawyer.modules import *

# massive_avaliation = False
# massive_avaliation = True

# SPLIT_SEMICOLON = massive_avaliation

for massive_evaluation in [False, True]:

    files_content = []
    files_base = []

    local_path = os.path.dirname(__file__)

    if massive_evaluation:
        local_path = os.path.join(local_path, "massive_avaliation")

    examples_dir = os.path.join(local_path, "examples")
    base_splitted_dir = os.path.join(local_path, "base_splitted")
    new_base_dir = os.path.join(local_path, "new_base")
    files = os.listdir(examples_dir)


    def dump_lines(base_path: str, lines: List[str]):
        out_path = Path(base_splitted_dir) / base_path.replace('.txt', '.base')
        with out_path.open(mode='w', encoding='utf8') as out_file:
            for line in lines:
                out_file.write(f'{line}\n')
        out_file.close()


    for file in sorted(files):
        example_name = ".".join(file.split(".")[0:-1])
        with open(os.path.join(examples_dir, file), "r", encoding="utf8") as fs:
            content = fs.read()
            files_content.append((file, content))

        base_file_name = example_name + ".base"
        base_file_path = os.path.join(base_splitted_dir, base_file_name)

        if os.path.exists(base_file_path):
            with open(base_file_path, "r", encoding="utf8") as fs:
                content = fs.readlines()
                files_base.append((file, content))
        else:
            files_base.append((file, ""))

    sentence_split = SentenceSplit(debug_log=True,
                                   modules=[ForceDropPageNumberLinesModule(), ReplaceModule(), ReplaceLongWordsModule(),
                                            ReplaceConcatenatedDotModule()])

    path_evaluation_file = os.path.join(local_path, "sentences_updated.txt")
    if os.path.exists(path_evaluation_file):
        os.remove(path_evaluation_file)

    for indice, file_content in enumerate(files_content):
        base = files_base[indice]
        assert base[0] == file_content[0]

        if base[0] == "0100314-53.2020.5.01.0501-2c75bd6.txt":
            stop_parar = ""

        text_splitted = sentence_split.get_sentences(file_content[1], split_by_semicolon=massive_evaluation)
        # Using stanza
        # text_splitted = sentence_spliter.get_sentences_with_stanza(file_content[1])

        file_name_written = False
        generate_base = False

        if base[1] == "":
            file_name_written = True
            generate_base = True

        if base[1] != "":
            for idx, sentence in enumerate(text_splitted):
                base_sentence = str(base[1][idx]).replace("\n", "")
                try:
                    assert sentence == base_sentence
                except:
                    fs = open(path_evaluation_file, mode="a", encoding='utf8')

                    if not file_name_written:
                        fs.write("\n" + file_content[0] + "\n")
                        file_name_written = True

                    fs.write(f"sentence {idx + 1} from base:\n")
                    fs.write(base_sentence + "\n")
                    fs.write("new_base:\n")
                    fs.write(sentence + "\n\n")
                    break

        if file_name_written:
            extension = ".new_base"
            if generate_base:
                extension = ".base"
            file_name = file_content[0].replace(".txt", "")
            result_file = os.path.join(new_base_dir, file_name + extension)

            try:
                with open(result_file, "w", encoding='utf8') as fs:
                    for text in text_splitted:
                        fs.write(text + "\n")
            except FileNotFoundError:
                print(
                    f'Problem evaluating {file_name} {"with" if massive_evaluation else "without"} '
                    f'massive evaluation'.strip()
                )
                continue

    sentence_split.generate_log()
    print(
        f"Test complete {'with' if massive_evaluation else 'without'} massive evaluation. "
        f"Check 'new_base' directory for changes."
    )
