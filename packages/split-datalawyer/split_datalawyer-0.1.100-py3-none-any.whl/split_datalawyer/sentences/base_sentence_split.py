import html

from pathlib import Path
from typing import Union, List

from split_datalawyer.modules import ForceDropPageNumberLinesModule, ReplaceModule, ReplaceLongWordsModule
from split_datalawyer.modules.modules_types import ModulesType
from split_datalawyer.utils import ABBREVIATION_LIST, get_stop_patterns


class BaseSentenceSplit:

    def __init__(self, stop_patterns_path: Union[str, Path] = None, debug_log: bool = False, modules: List = None,
                 minimum_word_count: int = 0, return_paragraphs: bool = False, debug_lines: bool = False,
                 debug_paragraphs: bool = False, remove_stop_phrases: bool = True, split_by_semicolon: bool = False,
                 split_parenthesis_ending: bool = True, split_by_hyphens: bool = False, limit: int = 300):
        if modules is None:
            modules = [ForceDropPageNumberLinesModule(), ReplaceModule(), ReplaceLongWordsModule()]
        self._list_stop_patterns = get_stop_patterns(stop_patterns_path)
        self._list_abbreviations = ABBREVIATION_LIST
        self._ending_abbreviations = ['etc', 'sp', 'cef', 'pr', 'pe', 'ltda']
        self._debug_log = debug_log
        self._debug_messages = []
        self._modules = modules
        self._minimum_word_count = minimum_word_count
        self._return_paragraphs = return_paragraphs
        self._debug_lines = debug_lines
        self._debug_paragraphs = debug_paragraphs
        self._remove_stop_phrase = remove_stop_phrases
        self._split_by_semicolon = split_by_semicolon
        # self._split_parenthesis_ending = split_parenthesis_ending
        self._split_by_hyphens = split_by_hyphens
        self._limit = limit

    def log(self, message: str):
        if self._debug_log:
            self._debug_messages.append(message)

    def _get_modules_by_type(self, module_type):
        modules = []

        for module in self._modules:
            if module.get_type() == module_type:
                modules.append(module)

        return modules

    def generate_log(self):
        if self._debug_log:
            with open("sentence_split_log.txt", mode='w', encoding='utf8') as log_file:
                for message in self._debug_messages:
                    log_file.write(message + "\n")

    def _preprocess_text(self, text: str):
        if (text is None) or text == "":
            return None
        text = html.unescape(text)
        replace_modules = self._get_modules_by_type(ModulesType.REPLACE)
        for module in replace_modules:
            text = module.transform(text)
        return text

    def _is_small_phrase(self, text: str):
        if self._minimum_word_count > 0:
            return len(text.split()) < self._minimum_word_count
        else:
            return False
