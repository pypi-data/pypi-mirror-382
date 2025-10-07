import re
from split_datalawyer.utils.file_utils import *
from split_datalawyer.utils.hyphen_utils import *


def _get_local_directory():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

    return dname


def get_stop_patterns(stop_patterns_path=None):
    if stop_patterns_path is None:
        stop_patterns_path = os.path.join(_get_local_directory(), "stoppatterns.txt")

    f = open(stop_patterns_path, encoding='utf-8')
    phrase_list = f.readlines()
    f.close()

    return [re.compile(x.replace("\n", ""), re.IGNORECASE) for x in phrase_list]


def _get_abbreviations(add_dot=True):
    abbreviations_path = os.path.join(_get_local_directory(), "abbreviations.csv")
    with open(abbreviations_path, "r", encoding='utf-8') as f:
        abbreviations = f.readlines()

    if add_dot:
        return [x.replace("\n", "").lower() + "." for x in abbreviations]
    else:
        return [x.replace("\n", "").lower() for x in abbreviations]


def _get_continuation_terms():
    continuation_terms_path = os.path.join(_get_local_directory(), "continuation_terms.csv")
    f = open(continuation_terms_path, "r", encoding='utf-8')
    continuation_terms = f.readlines()
    f.close()

    return [re.compile(x.replace("\n", "")) for x in continuation_terms]


ABBREVIATION_LIST = _get_abbreviations()
ABBREVIATION_LIST_WITHOUT_DOTS = _get_abbreviations(False)
CONTINUATION_TERMS = _get_continuation_terms()
DEFAULT_STOP_PATTERNS = get_stop_patterns()
