import locale
import re

from datetime import datetime
from typing import List
from split_datalawyer.utils.regex_utils import __REGEX_SECTION_NUMBERS__, __CNJ_NUMBER__, section_number_exceptions

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')


def parenthesis_is_closed(phrase: str) -> bool:
    if phrase.strip() != "":
        if phrase.count("(") > phrase.count(")") or phrase.rfind(")") < phrase.rfind("("):
            return False
    return True


def contains_only_closing_parenthesis(phrase: str) -> bool:
    return phrase.count("(") == 0 and phrase.count(")") > 0


def is_closing_a_parenthesis(phrase: str) -> bool:
    if any([phrase.strip().endswith(ending) for ending in [').', ');']]):
        return True
    return phrase.strip() != "" and not is_section_number(phrase.split()[0]) and (phrase.count(")") > phrase.count("("))


def is_valid_date_format(text: str) -> List[bool]:
    result = []
    for date_format in ["%d de %B de %Y"]:
        try:
            result.append(datetime.strptime(text, date_format) is not None)
        except ValueError:
            result.append(False)
    return result


def is_date_format(text: str) -> bool:
    return any(is_valid_date_format(text))


def match(text: str, regex: re.Pattern):
    return len(regex.findall(text)) > 0


def is_cnj_number(text: str) -> bool:
    return match(text=text, regex=__CNJ_NUMBER__)


def is_section_number(text: str) -> bool:
    return text.lower() not in section_number_exceptions and not is_cnj_number(text) and any(
        regex.match(text) for regex in __REGEX_SECTION_NUMBERS__
    )
