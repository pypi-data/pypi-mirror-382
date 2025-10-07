import re
import string

section_number_exceptions = ["a", "o", "e"]

item_replacement = '-'

__ENDING_PUNCTUATION_TUPLE__ = tuple([".", ";", ":", "\"", "!", "?", ")"])
__ALPHA_SECTION_NUMBER__ = re.compile(r"^[a-zA-Z]{1}\s*[\.\-\)]+$")
__REGEX_SECTION_NUMBERS__ = [re.compile(r"^[0-9]{1,}(\.[0-9]+)?[\.\-\)\s]+$"),  # "1.0.", "4.2.", "02.-"
                             re.compile(r"^[0-9]{1,}(\.[0-9]+)*[\.\-\)]*$"),  # "4.9"
                             re.compile(r"^([\.\-]*[MDCLXVI]{1,4}\s*[\.\-\)]?)$", re.IGNORECASE),  # "I.", "II."
                             re.compile(r"^(\([MDCLXVI]{1,4}\s*\))$", re.IGNORECASE),  # "(I)", "(ii)"
                             re.compile(r"^\(?[a-zA-Z]{1}\)?$"),
                             __ALPHA_SECTION_NUMBER__]  # "i)", "a)", "a-", "(i)"
__PAGE_NUMBERS__ = [re.compile(r"^Página [0-9]{1,} de [0-9]{1,}$", re.IGNORECASE),
                    re.compile(r"^[0-9]{1,} (de|of) [0-9]{1,}$", re.IGNORECASE),
                    re.compile(r"^Página([0-9]| [0-9])$", re.IGNORECASE),
                    re.compile(r"^Fls.:? [0-9]{1,}$", re.IGNORECASE),
                    re.compile(r"^ID.* Pág\.([0-9]{1,}| [0-9]{1,})$", re.IGNORECASE),
                    re.compile(r"^[0-9]{1,}\/[0-9]{1,}$", re.IGNORECASE)]
__DECIMAL_NUMBERS__ = re.compile(r"^[-+]?(?:\b[0-9]+(?:[,.]?[0-9]{3})*[,.][0-9]{2}\b)")
__OAB_NUMBER__ = re.compile(r"^(?:[0-9]+(?:[.]?[0-9]{3})*)$")
__URL__ = re.compile(r"(https|http):\/\/.*$")
__EMAIL__ = re.compile(r"[\w.-]+@[\w.-]+\.\w+$")
__LAW_NUMBERS__ = [re.compile(r"^(?:[0-9]+(?:[.][0-9]{3})+(?:[\/][0-9]{2,4})*)$")]
__SECTION_NUMBER__ = re.compile(r"^[0-9]{1,}(\.[0-9]+)?[\.\-\)]*$")  # "1.0.", "4.2.", "02.-, 1.0, 1-"
__CNJ_NUMBER__ = re.compile(r"\d{7}\-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}")
__CURRENCY__ = re.compile(r"^(?:R\$\s*)?(?:\d{1,3}(?:\.\d{3})*|\d+),\d{2}$")
__ELLIPSIS__ = re.compile(r"^[\"\'\“\”]?[\[\(]?\.{2,5}[\]\)]?")
__SPLIT_SPACES__ = re.compile(rf"([a-zA-Z]){item_replacement}\s+")
__HYPHEN_COMPOUND_CHECK__ = re.compile(rf"\w+-\s*\w+")
__HYPHEN_SPLIT_WORDS_CHECK__ = re.compile(rf"(\w+)-\s+(\w*)")
__PARENTHESIS_ENDING__ = re.compile(r"\)[\.\;]*\s*[`\"']?$")

punctuations = re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")

# Different quotes are used.
re_quotes_1 = re.compile(r"(?u)(^|\W)[´‘’′`']", re.UNICODE)
re_quotes_2 = re.compile(r"(?u)[´‘’`′'](\W|$)", re.UNICODE)
re_quotes_3 = re.compile(r'(?u)[´‘’`′“”]', re.UNICODE)
re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
re_tree_dots = re.compile(u'…', re.UNICODE)
# Different punctuation patterns are used.
re_changehyphen = re.compile(r"[-•●∙‣‒–—]", re.UNICODE)
re_doublequotes_1 = re.compile(r'(\"\")')
re_doublequotes_2 = re.compile(r'(\'\')')
re_trim = re.compile(r' +', re.UNICODE)
re_page_numbers = re.compile(r'(página|pagina|pág.|pag.)\s\d{1,4}\sde\s\d{1,4}', re.UNICODE | re.IGNORECASE)
re_dotted_line = re.compile(r'\.{5,}', re.UNICODE)

pattern_punctuation = re.compile(r'(?u)[' + str(string.punctuation) + ']', re.UNICODE)


def match(text: str, regex: re.Pattern):
    return len(regex.findall(text)) > 0


def is_cnj_number(text: str) -> bool:
    return match(text=text, regex=__CNJ_NUMBER__)


def is_currency(text: str) -> bool:
    """
    Validates if a string represents a Brazilian currency amount.
    Handles formats like: R$ 1.234,56 | 1.234,56 | 1234,56 | R$1234,56
    """
    return match(text=text, regex=__CURRENCY__)


def is_section_number(text: str) -> bool:
    return text.lower() not in section_number_exceptions and not is_cnj_number(text) and not is_currency(text) and \
        not text.lower().startswith('e-mail') and any(_regex.match(text) for _regex in __REGEX_SECTION_NUMBERS__)
