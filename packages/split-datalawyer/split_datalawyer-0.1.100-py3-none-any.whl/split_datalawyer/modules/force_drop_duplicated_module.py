from split_datalawyer.modules.modules_types import ModulesType
from split_datalawyer.utils.regex_utils import __PAGE_NUMBERS__


class ForceDropPageNumberLinesModule:

    def get_type(self):
        return ModulesType.DUPLICATED_CONDITION

    def evaluate(self, document_sentences):
        has_page_print_indicator = False

        for sentence in document_sentences:
            has_page_print_indicator = any(pattern.match(sentence) for pattern in __PAGE_NUMBERS__)

            if has_page_print_indicator:
                break

        return has_page_print_indicator
