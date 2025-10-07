import re

from collections import Counter
from pathlib import Path
from typing import Union, List

from split_datalawyer.modules.modules_types import ModulesType
from split_datalawyer.sentences.base_sentence_split import BaseSentenceSplit
from split_datalawyer.sentences.split_utils import split_by_sentence

from split_datalawyer.utils.regex_utils import is_cnj_number
from split_datalawyer.utils.pdf_utils import clean_text, is_upper, strip_punctuation, \
    starts_with_upper, starts_with_section_number, item_replacement, starts_with_ellipsis, \
    merge_split_words, merge_split_sections, load_pdf_lines_from_path, is_currency, ends_with_punctuation


class PDFSentenceSplit(BaseSentenceSplit):

    def __init__(self, stop_patterns_path: Union[str, Path] = None, debug_log: bool = False, modules: List = None,
                 minimum_word_count: int = 0, return_paragraphs: bool = False, debug_lines: bool = False,
                 debug_paragraphs: bool = False, remove_stop_phrases: bool = True, split_by_semicolon: bool = False,
                 split_parenthesis_ending: bool = True, split_by_hyphens: bool = False, limit: int = 300,
                 average_lines_per_page: int = 40):
        super().__init__(stop_patterns_path, debug_log, modules, minimum_word_count, return_paragraphs, debug_lines,
                         debug_paragraphs, remove_stop_phrases, split_by_semicolon, split_parenthesis_ending,
                         split_by_hyphens, limit)
        self._average_lines_per_page = average_lines_per_page

    def _is_stop_phrase(self, text: str) -> bool:
        page_number = text.isdigit()
        if page_number:
            self.log("page_number: " + text)
        return page_number or any(regex.match(text) for regex in self._list_stop_patterns)

    def _preprocess_text(self, text: str):
        if text is None or text.strip() == "":
            return None
        return re.sub(r"^\d{1,2}(\s?)$", r'\n', text, 0, re.MULTILINE)

    def _preprocess_line(self, line: str):
        if line is None:
            return None
        line = clean_text(line)
        for module in self._get_modules_by_type(ModulesType.REPLACE):
            line = module.transform(line)
        return line

    def get_sentences_from_path(self, pdf_path: Union[str, Path], split_parenthesis_ending: bool = True) -> List[str]:
        return self.get_sentences_from_lines(
            lines=load_pdf_lines_from_path(pdf_path), split_parenthesis_ending=split_parenthesis_ending
        )

    def get_sentences(self, text: str, split_parenthesis_ending: bool = True):
        text = self._preprocess_text(text)
        if text is not None:
            return self.get_sentences_from_lines(
                lines=text.splitlines(), split_parenthesis_ending=split_parenthesis_ending
            )
        else:
            return []

    def get_headers_footers(self, text: str) -> List[str]:

        lines = self._preprocess_text(text).splitlines()

        max_occurrences = max(2, int(len(lines) / self._average_lines_per_page / 2))

        lines = [self._preprocess_line(line) for line in lines]

        count = Counter(lines)

        return sorted(
            set(
                [line for line in lines if (len(line.strip()) > 0 and line in count and count[line] >= max_occurrences)]
            )
        )

    def get_sentences_from_lines(self, lines: List[str], split_parenthesis_ending: bool = True):

        max_occurrences = max(2, int(len(lines) / self._average_lines_per_page / 2))

        if self._debug_lines:
            for line in lines:
                self.log(self._preprocess_line(line))

        lines = [self._preprocess_line(line) for line in lines]

        count = Counter(lines)

        lines = [line for line in lines if line in count and count[line] < max_occurrences]
        lines = [sentence for line in lines for sentence in split_by_sentence(
            text=line,
            split_by_semicolon=self._split_by_semicolon,
            split_parenthesis_ending=split_parenthesis_ending,
            split_by_hyphens=self._split_by_hyphens,
            limit=self._limit
        )]

        paragraphs = []
        current_paragraph = ""

        for idx, line in enumerate(lines):
            if self._remove_stop_phrase and self._is_stop_phrase(line):
                continue
            if not line.strip():  # Verifica se a linha está em branco
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
            else:
                if is_upper(strip_punctuation(line)) or is_cnj_number(line) or is_currency(line):
                    if current_paragraph:
                        paragraphs.append(current_paragraph.strip())
                        current_paragraph = ""
                    paragraphs.append(line.strip())

                elif ends_with_punctuation(line) or (
                        0 <= idx <= self._average_lines_per_page and len(line.split(':')) == 2
                ):

                    if 0 <= idx <= self._average_lines_per_page:

                        if starts_with_upper(line) and line.endswith(':') or (len(line.split(':')) == 2):
                            if current_paragraph:
                                paragraphs.append(current_paragraph.strip())
                                current_paragraph = ""
                            paragraphs.append(line.strip())
                        else:
                            if starts_with_upper(line) and ends_with_punctuation(line):
                                if current_paragraph:
                                    paragraphs.append(current_paragraph.strip())
                                    current_paragraph = ""
                                paragraphs.append(line.strip())
                            else:
                                if current_paragraph:
                                    current_paragraph += line + " "
                                    paragraphs.append(current_paragraph.strip())
                                    current_paragraph = ""
                                else:
                                    paragraphs.append(line.strip())

                    else:

                        if starts_with_upper(line) and ends_with_punctuation(line):
                            if current_paragraph:
                                paragraphs.append(current_paragraph.strip())
                                current_paragraph = ""
                            paragraphs.append(line.strip())
                        else:
                            if current_paragraph:
                                current_paragraph += line + " "
                                paragraphs.append(current_paragraph.strip())
                                current_paragraph = ""
                            else:
                                paragraphs.append(line.strip())

                elif starts_with_section_number(line) or line.startswith(item_replacement) or starts_with_ellipsis(
                        line):
                    if current_paragraph:
                        paragraphs.append(current_paragraph.strip())
                        current_paragraph = ""
                    if ends_with_punctuation(line):
                        paragraphs.append(line.strip())
                    else:
                        current_paragraph += line + " "

                else:
                    current_paragraph += line + " "

        # Adicione o último parágrafo
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())

        # Agora, 'paragraphs' contém os parágrafos reconstruídos
        if self._debug_paragraphs:
            for paragraph in paragraphs:
                self.log("")
                self.log(paragraph)
                self.log("")

        if self._return_paragraphs:
            return [merge_split_words(paragraph) for paragraph in merge_split_sections(paragraphs)]

        return [
            merge_split_words(sentence) for sentence in
            merge_split_sections(split_by_sentence(
                text=paragraphs,
                split_by_semicolon=self._split_by_semicolon,
                split_parenthesis_ending=split_parenthesis_ending,
                split_by_hyphens=self._split_by_hyphens,
                limit=self._limit
            ))
        ]
