# From \datalawyer\jurimetria\utils\split_utils.py

import re
import string
import html
import pandas as pd

from typing import List

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters, PunktLanguageVars
from split_datalawyer.utils import ABBREVIATION_LIST_WITHOUT_DOTS, cached_path
from split_datalawyer.utils.regex_utils import __PARENTHESIS_ENDING__
from split_datalawyer.utils.utils import parenthesis_is_closed, is_closing_a_parenthesis

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


class JuridicoVars(PunktLanguageVars):
    sent_end_chars = ('.', '?', '!', ';')


punkt_param = PunktParameters()
punkt_param.abbrev_types = set(
    pd.read_csv(cached_path('https://s3.amazonaws.com/datalawyer-models/datalawyer/lista_abreviacoes_lower.csv'),
                header=None)[0].values)

punkt_param.abbrev_types.update(set(ABBREVIATION_LIST_WITHOUT_DOTS))

regex = re.compile('[%s]' % re.escape(string.punctuation))
substituicoes = {"Dr(a)": "Dr_a_", "Sr(a)": "Sr_a_", "Exmo(a)": "Exmo_a_"}
substituicoes_rev = {value: key for (key, value) in substituicoes.items()}


def _ends_with_parenthesis(text: str) -> bool:
    matches = __PARENTHESIS_ENDING__.findall(text)
    if len(matches) > 0:
        # if len(matches) == 0 or all([len(match) == 0 for match in matches]):
        return True
    return False


def _split_by_parenthesis(text: str) -> List[str]:
    results = []
    if '(' in text:
        fragments = text.split('(')
        for idx, fragment in enumerate(fragments):
            if idx == 0:
                if len(fragment.strip()) > 0:
                    results.append(fragment)
            elif idx < (len(fragments) - 1):
                if ')' in fragment:
                    sub_fragments = fragment.split(')')
                    results.append('(' + sub_fragments[0] + ')')
                    if len(sub_fragments) == 2:
                        results.append(sub_fragments[-1])
                    else:
                        results.append(')'.join(sub_fragments[1:]))
                else:
                    fragments[idx + 1] = fragment + fragments[idx + 1]
            else:
                results.append('(' + fragment)
    else:
        results.append(text)
    return results


def split_by_parenthesis(sentences: List[str]) -> List[str]:
    results = []
    for sentence in sentences:
        if _ends_with_parenthesis(sentence):
            results.extend(_split_by_parenthesis(sentence))
        else:
            results.append(sentence)
    return results


def _split_by_length(text: str, length: int) -> List[str]:
    words = text.split()
    return [' '.join(words[i:i + length]) for i in range(0, len(words), length)]


def split_by_length(sentences: List[str], split_by_semicolon: bool, limit: int) -> List[str]:
    results = []
    for sentence in sentences:
        if len(sentence.split()) > limit:
            if split_by_semicolon:
                results.extend(_split_by_length(text=sentence, length=limit))
            else:
                results.extend(split_by_sentence(text=sentence, split_by_semicolon=True,
                                                 split_parenthesis_ending=False, split_by_hyphens=False,
                                                 limit=limit))
        else:
            results.append(sentence)
    return results


def split_by_hyphen(sentences: List[str]) -> List[str]:
    results = []
    hyphens = [chr(code) for code in [8211]]
    for sentence in sentences:
        _split = False
        if not _ends_with_parenthesis(sentence):
            for hyphen in hyphens:
                if hyphen in sentence:
                    _split = True
                    results.extend(sentence.split(hyphen))
        if not _split:
            results.append(sentence)
    return results


# Replace periods in acronyms with a placeholder
acronym_pattern = re.compile(r'\b[A-Z](?:\.[A-Z])+\.?')

def protect_acronyms(text):

    def replace_dots(match):
        return match.group(0).replace('.', '<!DOT!>')

    return acronym_pattern.sub(replace_dots, text)


def restore_acronyms(text):
    return text.replace('<!DOT!>', '.')


def sentence_tokenize(sentence_tokenizer, text):
    result = []
    for sentence in sentence_tokenizer.tokenize(protect_acronyms(multi_replace(text, substituicoes, ignore_case=True))):
        result.append(restore_acronyms(multi_replace(sentence, substituicoes_rev, ignore_case=True)))
    return result


def multi_replace(string, replacements, ignore_case=False):
    """
    Given a string and a dict, replaces occurrences of the dict keys found in the
    string, with their corresponding values. The replacements will occur in "one pass",
    i.e. there should be no clashes.
    :param str string: string to perform replacements on
    :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
    :param bool ignore_case: whether to ignore case when looking for matches
    :rtype: str the replaced string
    """
    if ignore_case:
        replacements = dict((pair[0].lower(), pair[1]) for pair in sorted(replacements.items()))
    rep_sorted = sorted(replacements, key=lambda s: (len(s), s), reverse=True)
    rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
    pattern = re.compile("|".join(rep_escaped), re.I if ignore_case else 0)
    return pattern.sub(lambda match: replacements[match.group(0).lower() if ignore_case else match.group(0)], string)


def split_by_break(text: str):
    _text = re.sub(r'[“”]', '"', text)
    return [sentence.strip() for sentence in _text.splitlines()]


def startswith(quote_char, trecho, text):
    return text.startswith(quote_char + trecho)


def sanitize_split(text: str) -> str:
    quote_chars = ['"', '\'']
    trechos = [' (...),', ' (...);', ' (...)', '(...)', '[...]', '...,', '..,', ' ...,', ' ..,', ' ...', '...', '()',
               '),', ');', ')', ' ,', ' ;', ' -', '•', ',', ';', '.']
    text = text.strip()
    for quote_char in quote_chars:
        for trecho in trechos:
            if text.count(quote_char) == 1:
                if startswith(quote_char, trecho, text):
                    text = text.replace(quote_char + trecho, '')
            elif text.count(quote_char) == 2:
                if text.startswith(quote_char):
                    if text.endswith(quote_char):
                        text = text[1:-1]
                        assert text.count(quote_char) == 0
                        text = text.replace(trecho, '')
                    elif text.endswith(quote_char + '.'):
                        text = text[1:-2] + "."
                        assert text.count(quote_char) == 0
                        text = text.replace(trecho, '')
        if text.startswith(quote_char):
            patterns = ['\d+\.*', '^(\-*\d\s*\.*)*\-*\)*']
            for pattern in patterns:
                if re.fullmatch(pattern, text[1:]):
                    text = re.sub(pattern, '', text)[1:]
    return text.strip()


def _close_parenthesis(sentences: List[str], tolerance: int = 7) -> List[str]:
    for_removal: List[int] = []
    initial_idx, count = None, None
    for idx, sentence in enumerate(sentences):
        if initial_idx is not None:
            count += 1
        if not parenthesis_is_closed(sentence):
            count = 0
            initial_idx = idx
            continue
        if initial_idx is not None and is_closing_a_parenthesis(sentence):
            joined_sentences = " ".join(sentences[initial_idx:idx + 1])
            sentences[initial_idx] = joined_sentences
            for_removal.extend([_idx for _idx in range(initial_idx + 1, idx + 1)])
            initial_idx, count = None, None
        if count is not None and count >= tolerance:
            initial_idx, count = None, None
    for _idx in for_removal:
        sentences[_idx] = None
    return split_by_parenthesis(
        [sentence for sentence in sentences if (sentence is not None and len(sentence.strip()) > 0)])


def split_by_sentence(text, split_by_semicolon=False, split_parenthesis_ending: bool = False,
                      split_by_hyphens: bool = False, limit: int = 500):
    if split_by_semicolon:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param, lang_vars=JuridicoVars())
    else:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param)
    if isinstance(text, str):
        text = re.sub(r'[“”]', '"', text)
        text = html.unescape(text)
        sentences = [sanitize_split(sentence) for sentence in sentence_tokenize(sentence_tokenizer, text)]
        if split_parenthesis_ending:
            sentences = split_by_parenthesis(sentences)
        sentences = split_by_length(sentences, split_by_semicolon, limit)
        if split_by_hyphens:
            sentences = split_by_hyphen(sentences)
        return sentences
    elif isinstance(text, Iterable):
        result = []
        for subtext in text:
            subtext = re.sub(r'[“”]', '"', subtext)
            result.extend(split_by_sentence(text=subtext, split_by_semicolon=split_by_semicolon,
                                            split_parenthesis_ending=split_parenthesis_ending,
                                            split_by_hyphens=split_by_hyphens, limit=limit))
        if split_parenthesis_ending:
            result = _close_parenthesis(result)
        return result


def split(text, split_by_semicolon=False, split_parenthesis_ending: bool = False,
          split_by_hyphens: bool = False, limit: int = 500):
    segments_by_break = split_by_break(text)
    return split_by_sentence(text=segments_by_break, split_by_semicolon=split_by_semicolon,
                             split_parenthesis_ending=split_parenthesis_ending, split_by_hyphens=split_by_hyphens,
                             limit=limit)
