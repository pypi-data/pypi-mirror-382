import re

__PORTUGUESE_LONG_WORDS__ = [
    "Pneumoultramicroscopicossilicovulcanoconiótico",
    "Hipopotomonstrosesquipedaliofobia",
    "Anticonstitucionalissimamente",
    "Oftalmotorrinolaringologista",
    "Cineangiocoronariográfico",
    "Dacriocistossiringotomia",
    "Desconstitucionalização",
    "Histerossalpingográfico",
    "Anticonstitucionalmente"
]

from split_datalawyer.modules import ModulesType


class ReplaceLongWordsModule:

    def __init__(self):
        self.limit = 22

    def get_type(self):
        return ModulesType.REPLACE

    def is_long_word(self, word: str) -> bool:
        return len(word) >= self.limit

    def transform(self, text):
        long_words = re.findall(r"\w{22,}", text)

        for word in long_words:
            if word not in __PORTUGUESE_LONG_WORDS__:
                text = re.sub(word, "", text)

        return text
