import re
import os

from split_datalawyer.modules import ModulesType
from split_datalawyer.utils import ABBREVIATION_LIST_WITHOUT_DOTS

IGNORE_PARTS = ["n.º"]


class ReplaceConcatenatedDotModule():
    def __init__(self):
        self._PATTERN = re.compile(r" \w+\.\w+ ")

    def get_type(self):
        return ModulesType.REPLACE

    def transform(self, text: str):
        incorrect_strech = self._PATTERN.findall(text)
        for strech in incorrect_strech:
            strech = str(strech).strip()
            should_not_ignore = str(strech).lower() not in IGNORE_PARTS
            is_not_abbreviation = str(strech).lower() not in ABBREVIATION_LIST_WITHOUT_DOTS
            if should_not_ignore and is_not_abbreviation:
                parts = strech.split(".")
                if len(parts) == 2:
                    if len(parts[0]) > 2:
                        old_text = strech
                        new_text = str(parts[0]) + ". " + str(parts[1])
                        text = text.replace(old_text, new_text)
        return text
