import re

__TERMS_TO_REPLACE__ = [
    "\x00",  # NULL
]

from split_datalawyer.modules import ModulesType


class ReplaceModule:

    def get_type(self):
        return ModulesType.REPLACE

    def transform(self, text):
        patterns = [re.compile(x) for x in __TERMS_TO_REPLACE__]
        for pattern in patterns:
            text = pattern.sub("", text)

        return text
