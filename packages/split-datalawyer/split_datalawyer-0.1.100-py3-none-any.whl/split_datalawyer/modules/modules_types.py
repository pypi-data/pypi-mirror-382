from enum import Enum


class ModulesType(Enum):
    DUPLICATED_CONDITION = 0
    REPLACE = 1


class ConditionalModule:
    def evaluate(self):
        return False


class ReplaceModule:
    def transform(self, text):
        return text
