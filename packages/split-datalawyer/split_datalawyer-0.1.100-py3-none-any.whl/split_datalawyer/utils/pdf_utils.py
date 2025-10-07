# #!/usr/bin/env python
# # coding: utf-8

import fitz
import re
import html

from typing import List, Union
from pathlib import Path

from split_datalawyer.utils.regex_utils import __SPLIT_SPACES__, re_tree_dots, re_dotted_line, re_changehyphen, \
    re_quotes_1, re_quotes_2, re_quotes_3, re_dots, re_punctuation, re_doublequotes_1, re_doublequotes_2, re_trim, \
    item_replacement, re_page_numbers, pattern_punctuation, __ELLIPSIS__, match, is_section_number, is_currency
from split_datalawyer.utils.hyphen_utils import is_long_word, get_possible_split_words, get_possible_compound_spans, \
    should_preserve_hyphen

final_punctuations = '.;:")?!'


def is_section_number_span(word_1: str, word_2: str) -> bool:
    return is_section_number(f'{word_1}-') or (is_section_number(word_1) and word_2.startswith('-'))


def merge_split_words(content: str) -> str:
    if not content.upper() == content:
        for possible_span in get_possible_compound_spans(content):
            for possible_split_words in get_possible_split_words(possible_span):
                if is_section_number_span(possible_split_words[0], possible_split_words[1]):
                    continue
                elif should_preserve_hyphen(possible_span):
                    continue
                elif is_long_word(possible_span):
                    continue
                elif possible_split_words[1][0].isupper() and not possible_split_words[1].startswith('-'):
                    # Likely a proper noun, so we should not merge the split words
                    continue
                else:
                    # Not a section number, so we can merge the split words
                    content = content.replace(possible_span, __SPLIT_SPACES__.sub(r"\1", possible_span))
                    # print(f"Replaced hyphen from {possible_span} in {content}")
    return content


def clean_text(text):
    """Apply all regex above to a given string."""
    text = html.unescape(text)
    text = text.replace('\xa0', ' ')
    text = re_tree_dots.sub('...', text)
    text = re_dotted_line.sub('.....', text)
    text = re_changehyphen.sub(item_replacement, text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re_dots.sub('.', text)
    text = re_punctuation.sub(r'\1', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    text = re_trim.sub(' ', text)
    text = replace_chars_in_interval(text, 61000, 128000, item_replacement)
    text = replace_chars_in_interval(text, 127, 159, '')
    text = re.sub(r'\s+', ' ', text)
    text = re_page_numbers.sub('', text)
    return text.strip()


def is_upper(text: str, strip_non_alpha: bool = True) -> bool:
    if strip_non_alpha:
        return re.sub('[^A-Za-z0-9]+', '', text).isupper()
    else:
        return text.isupper()


def is_lower(text: str, strip_non_alpha: bool = True) -> bool:
    if strip_non_alpha:
        return re.sub('[^A-Za-z0-9]+', '', text).islower()
    else:
        return text.islower()


def starts_with_upper(text: str) -> bool:
    return len(text.strip()) > 0 and is_upper(text[0])


def starts_with_lower(text: str) -> bool:
    return len(text.strip()) > 0 and is_lower(text[0])


def ends_with_final_punctuation(text: str) -> bool:
    return any([text.endswith(punctuation) for punctuation in final_punctuations])


def strip_punctuation(word: str) -> str:
    return re.sub(pattern_punctuation, ' ', word)


def ends_with_punctuation(text: str) -> bool:
    return len(text.strip()) > 0 and match(text=text[-1], regex=pattern_punctuation)


def starts_with_section_number(text: str) -> bool:
    return len(text.strip()) > 0 and is_section_number(text.split()[0])


def starts_with_ellipsis(text: str) -> bool:
    return match(text, __ELLIPSIS__)


keep_codes = [8, 9, 10, 13, 730, 8208, 8209, 8210, 8211, 8212, 8213, 8214, 8216, 8217, 8218, 8219, 8220, 8221, 8222,
              8223, 8226, 8230]


def clean_non_ascii_characters(text: str) -> str:
    return ''.join([i if (31 < ord(i) < 256 or ord(i) in keep_codes) else '' for i in text]).strip()


def replace_chars_in_interval(text, start, end, replacement):
    result = []
    for char in text:
        char_code = ord(char)
        if start <= char_code <= end:
            result.append(replacement)
        else:
            result.append(char)
    return ''.join(result)


def extract_pdf_text(pdf_path: Union[str, Path]) -> str:
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text += page.get_text(sort=True)
    return text


def split_pdf_lines(text: str) -> List[str]:
    return re.sub(r"^\d{1,2}(\s?)$", r'\n', text, 0, re.MULTILINE).splitlines()


def load_pdf_lines_from_path(pdf_path: Union[str, Path]) -> List[str]:
    return split_pdf_lines(extract_pdf_text(pdf_path))


def merge_split_sections(paragraphs: List[str]) -> List[str]:
    # Regex to check if a paragraph ends with a hyphen not preceded by a space
    # This catches cases like "word-" but not "word -"
    hyphen_pattern = re.compile(r'\S-$')
    # Merge paragraphs that appear to be section numbers with the following sentence
    merged = []
    i = 0
    while i < len(paragraphs):
        if is_section_number(paragraphs[i]):
            if (i + 1) < len(paragraphs):
                if ((not is_section_number(paragraphs[i + 1]) or is_currency(paragraphs[i + 1]))
                        and not paragraphs[i + 1].startswith(item_replacement)):
                    merged.append(paragraphs[i] + ' ' + paragraphs[i + 1])
                    i += 2
                else:
                    merged.append(paragraphs[i])
                    i += 1
            else:
                merged.append(paragraphs[i])
                i += 1

        elif starts_with_lower(paragraphs[i]) and not starts_with_section_number(paragraphs[i]):

            if i == 0:
                merged.append(paragraphs[i])
                i += 1
            else:
                merged[-1] = merged[-1] + ' ' + paragraphs[i]
                i += 1

        elif hyphen_pattern.search(paragraphs[i]):
            # Handle paragraphs ending with hyphen (word split across lines)
            if (i + 1) < len(paragraphs):
                # Remove the hyphen and merge with next paragraph
                # current_without_hyphen = paragraphs[i][:-1]  # Remove the trailing hyphen
                current_without_hyphen = paragraphs[i]  # Remove the trailing hyphen
                merged.append(current_without_hyphen + paragraphs[i + 1])
                i += 2
            else:
                # If it's the last paragraph, keep it as is
                merged.append(paragraphs[i])
                i += 1

        else:
            merged.append(paragraphs[i])
            i += 1

    return merged


def debug_line_count(pdf_path: Union[str, Path], print_page_number: int = None):
    pdf_document = fitz.open(pdf_path)
    lines_lengths = []
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        if print_page_number and page_number == print_page_number:
            for line in page.get_text().splitlines():
                print(line)
        lines_lengths.append(len(page.get_text().splitlines()))
        print(f'Page {page_number}: {len(page.get_text().splitlines())} lines and {len(page.get_text_blocks())} blocks')
    print(sum(lines_lengths) / len(lines_lengths))
