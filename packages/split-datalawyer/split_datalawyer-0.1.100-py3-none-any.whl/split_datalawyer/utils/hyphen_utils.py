#!/usr/bin/env python
# coding: utf-8

import re
import string
from typing import List
from dataclasses import dataclass
from split_datalawyer.utils.regex_utils import __HYPHEN_COMPOUND_CHECK__, __HYPHEN_SPLIT_WORDS_CHECK__, \
    is_section_number

mesoclysis_pattern = re.compile(
    r'^[a-záàâãéêíóôõúç]+-(?:me|te|se|o|a|lhe|nos|vos|os|as|lhes|la|lo)-[a-záàâãéêíóôõúç]+$')
mesoclysis_parts_pattern = re.compile(
    r'^([a-záàâãéêíóôõúç]+)-(me|te|se|o|a|lhe|nos|vos|os|as|lhes|la|lo)-([a-záàâãéêíóôõúç]+)$')


def is_mesoclysis(word: str) -> bool:
    """
    Check if a word contains mesoclysis (pronoun insertion in the middle of a verb).

    Mesoclysis in Portuguese typically appears with hyphens separating:
    verb_stem + hyphen + pronoun + hyphen + verb_ending

    Args:
        word (str): The word to check

    Returns:
        bool: True if mesoclysis is detected, False otherwise
    """

    # Pattern for mesoclysis: stem-pronoun-ending
    # Common clitic pronouns: me, te, se, o, a, lhe, nos, vos, os, as, lhes
    # Appears in future and conditional tenses

    return bool(mesoclysis_pattern.match(word.lower()))


def find_mesoclysis_parts(word):
    """
    Extract the parts of a mesoclytic word: stem, pronoun, ending

    Args:
        word (str): The word to analyze

    Returns:
        tuple: (stem, pronoun, ending) if mesoclysis found, None otherwise
    """

    match = mesoclysis_parts_pattern.match(word.lower())
    if match:
        return match.groups()
    return None


@dataclass
class CompoundAnalysis:
    is_compound: bool
    reasoning: List[str]
    confidence: float


class PortugueseCompoundDetector:
    def __init__(self):
        # Common prefixes that often form compound adjectives
        self.prefixes = {
            'anti', 'auto', 'contra', 'extra', 'inter', 'intra', 'multi', 'neo', 'non', 'para',
            'pós', 'pré', 'pro', 'pseudo', 'semi', 'sobre', 'sub', 'super', 'trans', 'ultra',
            'meta', 'micro', 'macro', 'mini', 'maxi', 'mono', 'bi', 'tri', 'poli', 'omni',
            'pan', 'proto', 'retro', 'vice', 'co', 'ex', 'hiper', 'hipo', 'infra', 'supra',
            'porta', 'bem', 'guarda', 'psico'
        }

        # Adjective suffixes (masculine/feminine/plural variations)
        self.adjective_suffixes = {
            'al', 'ais', 'ar', 'ares', 'ário', 'ária', 'ários', 'árias',
            'ativo', 'ativa', 'ativos', 'ativas', 'ável', 'áveis', 'ível', 'íveis',
            'ante', 'antes', 'ente', 'entes', 'inte', 'intes',
            'ico', 'ica', 'icos', 'icas', 'ético', 'ética', 'éticos', 'éticas',
            'oso', 'osa', 'osos', 'osas', 'udo', 'uda', 'udos', 'udas',
            'eiro', 'eira', 'eiros', 'eiras', 'ório', 'ória', 'órios', 'órias',
            'ivo', 'iva', 'ivos', 'ivas', 'ano', 'ana', 'anos', 'anas',
            'ense', 'enses', 'ês', 'esa', 'eses', 'esas', 'ino', 'ina', 'inos', 'inas'
        }

        # Color adjectives
        self.color_adjectives = {
            'azul', 'azuis', 'verde', 'verdes', 'amarelo', 'amarela', 'amarelos', 'amarelas',
            'vermelho', 'vermelha', 'vermelhos', 'vermelhas', 'branco', 'branca', 'brancos', 'brancas',
            'preto', 'preta', 'pretos', 'pretas', 'cinza', 'cinzas', 'rosa', 'rosas',
            'roxo', 'roxa', 'roxos', 'roxas', 'laranja', 'laranjas', 'violeta', 'violetas',
            'marrom', 'marrons', 'bege', 'beges', 'dourado', 'dourada', 'dourados', 'douradas',
            'prateado', 'prateada', 'prateados', 'prateadas', 'escuro', 'escura', 'escuros', 'escuras',
            'claro', 'clara', 'claros', 'claras'
        }

        # Field/domain terms
        self.field_terms = {
            'médico', 'médica', 'médicos', 'médicas', 'jurídico', 'jurídica', 'jurídicos', 'jurídicas',
            'político', 'política', 'políticos', 'políticas', 'econômico', 'econômica', 'econômicos', 'econômicas',
            'social', 'sociais', 'cultural', 'culturais', 'histórico', 'histórica', 'históricos', 'históricas',
            'científico', 'científica', 'científicos', 'científicas', 'técnico', 'técnica', 'técnicos', 'técnicas',
            'artístico', 'artística', 'artísticos', 'artísticas', 'físico', 'física', 'físicos', 'físicas',
            'mental', 'mentais', 'psicológico', 'psicológica', 'psicológicos', 'psicológicas',
            'biológico', 'biológica', 'biológicos', 'biológicas', 'químico', 'química', 'químicos', 'químicas',
            'filosófico', 'filosófica', 'filosóficos', 'filosóficas', 'teológico', 'teológica', 'teológicos',
            'teológicas', 'pedagógico', 'pedagógica', 'pedagógicos', 'pedagógicas', 'didático', 'didática', 'didáticos',
            'didáticas', 'clínico', 'clínica', 'clínicos', 'clínicas', 'cirúrgico', 'cirúrgica', 'cirúrgicos',
            'cirúrgicas', 'terapêutico', 'terapêutica', 'terapêuticos', 'terapêuticas', 'diagnóstico', 'diagnóstica',
            'diagnósticos', 'diagnósticas', 'fático', 'decreto', 'auxílio', 'má', 'boa', 'seguro', 'guarda', 'decreto',
            'aviso', 'licença', 'licenças'
        }

        # Geographic patterns
        self.geographic_patterns = {
            'brasileiro', 'brasileira', 'brasileiros', 'brasileiras', 'americano', 'americana', 'americanos',
            'americanas', 'europeu', 'europeia', 'europeus', 'europeias', 'asiático', 'asiática', 'asiáticos',
            'asiáticas', 'africano', 'africana', 'africanos', 'africanas', 'sul', 'norte', 'leste', 'oeste',
            'oriental', 'orientais', 'ocidental', 'ocidentais', 'meridional', 'meridionais',
            'setentrional', 'setentrionais', 'central', 'centrais', 'regional', 'regionais',
            'nacional', 'nacionais', 'internacional', 'internacionais', 'continental', 'continentais',
            'anglo', 'franco', 'greco', 'indo', 'luso', 'teuto', 'afro', 'sino', 'russo', 'italo',
            'hispano', 'germano',
        }

        # Semantic groups that commonly form compounds
        self.semantic_groups = {
            # Time-related
            'temporal', 'temporais', 'histórico', 'moderno', 'contemporâneo', 'atual', 'antigo', 'novo',
            # Size/dimension
            'grande', 'pequeno', 'alto', 'baixo', 'largo', 'estreito', 'longo', 'curto',
            # Quality/state
            'bom', 'mau', 'forte', 'fraco', 'rico', 'pobre', 'jovem', 'velho',
            # Professional/occupational
            'profissional', 'ocupacional', 'comercial', 'industrial', 'agrícola', 'urbano', 'rural',
            # Abstract concepts
            'conceitual', 'teórico', 'prático', 'abstrato', 'concreto', 'real', 'virtual'
        }

        punctuation = ''.join([_punct for _punct in string.punctuation if _punct != '-'])
        self.pattern_punctuation = re.compile(r'(?u)[' + punctuation + ']')

    def strip_punctuation(self, word: str) -> str:
        return re.sub(self.pattern_punctuation, ' ', word)

    def is_compound_adjective(self, word: str) -> bool:
        """
        Simple method that returns True if the word is detected as a compound adjective.
        
        Args:
            word (str): The word to analyze
            
        Returns:
            bool: True if compound adjective, False otherwise
        """
        analysis = self.analyze_compound(word)
        return analysis.is_compound

    def analyze_compound(self, word: str) -> CompoundAnalysis:
        """
        Comprehensive method that analyzes a word and returns detailed reasoning.
        
        Args:
            word (str): The word to analyze
            
        Returns:
            CompoundAnalysis: Detailed analysis with reasoning and confidence
        """
        word = self.strip_punctuation(word).strip().lower()
        reasoning = []
        confidence = 0.0

        # Check if word contains hyphen
        if '-' not in word:
            return CompoundAnalysis(False, ["No hyphen found"], 0.0)

        # Split by hyphen
        parts = word.split('-')

        left_part, right_part = parts[0], parts[1]

        # Check minimum length (avoid single letters or very short combinations)
        if len(left_part) < 2 or len(right_part) < 2:
            reasoning.append("Parts too short to be meaningful compound")
            return CompoundAnalysis(False, reasoning, 0.2)

        # Check if both parts look like Portuguese words (basic heuristic)
        if not self._looks_like_portuguese_word(left_part) or not self._looks_like_portuguese_word(right_part):
            reasoning.append("One or both parts don't follow Portuguese word patterns")
            return CompoundAnalysis(False, reasoning, 0.3)

        # Analyze left part
        left_analysis = self._analyze_part(left_part, "left")
        reasoning.extend(left_analysis['reasons'])
        confidence += left_analysis['confidence']

        # Analyze right part
        right_analysis = self._analyze_part(right_part, "right")
        reasoning.extend(right_analysis['reasons'])
        confidence += right_analysis['confidence']

        # Check for common compound patterns
        pattern_analysis = self._analyze_patterns(left_part, right_part)
        reasoning.extend(pattern_analysis['reasons'])
        confidence += pattern_analysis['confidence']

        # Final confidence normalization
        confidence = min(confidence / 3, 1.0)  # Average and cap at 1.0

        is_compound = confidence > 0.15

        return CompoundAnalysis(is_compound, reasoning, confidence)

    def _looks_like_portuguese_word(self, word: str) -> bool:
        """Check if a word follows basic Portuguese orthographic patterns."""
        # Portuguese uses these characters
        portuguese_pattern = re.compile(r'^[a-záàâãéêíóôõúçü]+$')

        # Check basic pattern
        if not portuguese_pattern.match(word):
            return False

        # Avoid common non-Portuguese patterns
        if re.search(r'[kwy]', word):  # These letters are rare in Portuguese
            return False

        # Check for reasonable vowel/consonant distribution
        vowels = len(re.findall(r'[aeiouáàâãéêíóôõú]', word))
        consonants = len(word) - vowels

        if vowels == 0 or consonants == 0:  # Must have both
            return False

        return True

    def _analyze_part(self, part: str, position: str) -> dict:
        """Analyze a single part of the compound word."""
        reasons = []
        confidence = 0.0

        # Check if it's a known prefix (mainly for left part)
        if position == "left" and part in self.prefixes:
            reasons.append(f"'{part}' is a recognized prefix")
            confidence += 0.8

        # Check if it's a color adjective
        if part in self.color_adjectives:
            reasons.append(f"'{part}' is a color adjective")
            confidence += 0.6

        # Check if it's a field term
        if part in self.field_terms:
            reasons.append(f"'{part}' is a domain/field term")
            confidence += 0.7

        # Check if it's a geographic term
        if part in self.geographic_patterns:
            reasons.append(f"'{part}' is a geographic term")
            confidence += 0.6

        # Check if it's in semantic groups
        if part in self.semantic_groups:
            reasons.append(f"'{part}' belongs to common semantic groups for compounds")
            confidence += 0.5

        return {'reasons': reasons, 'confidence': confidence}

    def _analyze_patterns(self, left: str, right: str) -> dict:
        """Analyze common compound patterns between the two parts."""
        reasons = []
        confidence = 0.0

        # Common semantic combinations
        semantic_combinations = [
            # Prefix + field
            (self.prefixes, self.field_terms),
            # Color + adjective
            (self.color_adjectives, self.adjective_suffixes),
            # Geographic + field
            (self.geographic_patterns, self.field_terms),
            # Field + field
            (self.field_terms, self.field_terms)
        ]

        for left_set, right_set in semantic_combinations:
            if left in left_set and (right in right_set or any(
                    right.endswith(suffix) for suffix in right_set if isinstance(right_set, set))):
                reasons.append(f"Common semantic combination: {type(left_set).__name__} + {type(right_set).__name__}")
                confidence += 0.5
                break

        # Check for coordinate compounds (both parts similar type)
        if left in self.field_terms and right in self.field_terms:
            reasons.append("Both parts are field/domain terms (coordinate compound)")
            confidence += 0.6

        # Check for morphological agreement (same gender/number endings)
        if self._check_agreement(left, right):
            reasons.append("Parts show morphological agreement")
            confidence += 0.4

        return {'reasons': reasons, 'confidence': confidence}

    def _check_agreement(self, left: str, right: str) -> bool:
        """Check if both parts have compatible endings (gender/number agreement)."""
        # Common ending pairs that indicate agreement
        agreement_patterns = [
            ('o', 'o'), ('a', 'a'), ('os', 'os'), ('as', 'as'),
            ('ico', 'ico'), ('ica', 'ica'), ('icos', 'icos'), ('icas', 'icas'),
            ('al', 'al'), ('ais', 'ais'), ('ário', 'ário'), ('ária', 'ária')
        ]

        for left_end, right_end in agreement_patterns:
            if left.endswith(left_end) and right.endswith(right_end):
                return True

        return False


def is_long_word(word: str) -> bool:
    return len(word) > 22


class PortugueseHyphenDetector:
    def __init__(self):
        # Oblique pronouns (clitic pronouns)
        self.oblique_pronouns = {
            # Direct object pronouns
            'me', 'te', 'o', 'a', 'se', 'nos', 'vos', 'os', 'as',
            # Indirect object pronouns
            'lhe', 'lhes',
            # Combined forms
            'mo', 'ma', 'mos', 'mas', 'to', 'ta', 'tos', 'tas',
            'lho', 'lha', 'lhos', 'lhas', 'no', 'na', 'nos', 'nas',
            'vo', 'va', 'vos', 'vas', 'lo', 'la', 'los', 'las'
        }

        # Compound prefixes (very comprehensive list)
        self.prefixes = {
            # Common prefixes
            'anti', 'ante', 'auto', 'contra', 'entre', 'extra', 'hiper', 'inter',
            'intra', 'mega', 'meta', 'micro', 'mini', 'multi', 'neo', 'pan',
            'para', 'pós', 'pré', 'pró', 'proto', 'pseudo', 'quasi', 'semi',
            'sobre', 'sub', 'super', 'supra', 'trans', 'ultra', 'vice', 'porta',

            # Greek and Latin prefixes
            'aero', 'agro', 'andro', 'antropo', 'arqui', 'astro', 'audio',
            'biblio', 'bio', 'cardio', 'centro', 'crono', 'demo', 'eco',
            'eletro', 'euro', 'foto', 'geo', 'hidro', 'homo', 'macro',
            'mono', 'morfo', 'neuro', 'paleo', 'poli', 'psico', 'radio',
            'retro', 'socio', 'tele', 'termo', 'xeno', 'zoo',

            # Numerical prefixes
            'uni', 'bi', 'tri', 'tetra', 'penta', 'hexa', 'hepta', 'octa',
            'nona', 'deca', 'centi', 'mili', 'kilo',

            # Less common but important prefixes
            'anglo', 'franco', 'greco', 'indo', 'luso', 'teuto', 'afro',
            'sino', 'russo', 'italo', 'hispano', 'germano',

            # Medical/scientific prefixes
            'cardio', 'gastro', 'hemato', 'hepato', 'neuro', 'pneumo',
            'dermato', 'oftalmo', 'otorrino', 'traumato',

            # Architectural/spatial prefixes
            'archi', 'infra', 'circum', 'peri', 'epi',

            # Common prefixes that require hyphen
            'anti', 'auto', 'contra', 'extra', 'infra', 'intra', 'mega',
            'multi', 'neo', 'pan', 'proto', 'pseudo', 'semi', 'sobre',
            'super', 'supra', 'ultra', 'inter', 'hiper', 'sub', 'pré',
            'pós', 'pró', 're', 'co', 'ex', 'vice', 'não', 'bem',
            'mal', 'além', 'aquém', 'recém', 'sem', 'sota', 'soto',
            'vizo', 'micro', 'macro', 'mini', 'maxi', 'homo', 'hetero',
            'mono', 'bi', 'tri', 'tetra', 'penta', 'hexa', 'hepta',
            'octa', 'nona', 'deca', 'uni', 'pluri', 'multi', 'omni',
            'ante', 'circum', 'trans', 'per', 'para', 'meta', 'sul', 'norte',
            'guarda', 'decreto', 'auxílio', 'má', 'boa', 'aviso', 'licença', 'licenças'
        }

        # Kinship terms
        self.kinship_terms = {
            'avô', 'avó', 'bisavô', 'bisavó', 'tataravô', 'tataravó',
            'pai', 'mãe', 'padrasto', 'madrasta', 'sogro', 'sogra',
            'genro', 'nora', 'cunhado', 'cunhada', 'primo', 'prima',
            'tio', 'tia', 'sobrinho', 'sobrinha', 'filho', 'filha',
            'irmão', 'irmã', 'meio', 'meia', 'enteado', 'enteada',

            # Direct family
            'neto', 'neta', 'bisneto', 'bisneta', 'tataravô', 'tataravó',

            # In-laws and step relations
            'compadre', 'comadre', 'padrinho', 'madrinha', 'afilhado', 'afilhada',
        }

        # Compound suffixes
        self.suffixes = {
            # Common suffixes
            'açu', 'guaçu', 'mirim', 'mor', 'açú', 'mirin', 'chave', 'base',

            # Ordinal suffixes
            'ésimo', 'ésima',

            # Augmentative/diminutive
            'zinho', 'zinha', 'zão', 'zona',

            # Professional/occupational
            'mestre', 'chefe', 'diretor', 'geral',

            # Geographic suffixes (Tupi-Guarani origin)
            'aba', 'ara', 'ema', 'etá', 'iba', 'oca', 'ová', 'tiba', 'tuba', 'una',
        }

        # Portuguese number words
        self.number_words = {
            # Cardinals
            'um', 'uma', 'dois', 'duas', 'três', 'quatro', 'cinco', 'seis',
            'sete', 'oito', 'nove', 'dez', 'onze', 'doze', 'treze', 'catorze',
            'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove', 'vinte',
            'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta',
            'noventa', 'cem', 'cento', 'duzentos', 'trezentos', 'quatrocentos',
            'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos',
            'mil', 'milhão', 'bilhão', 'trilhão',

            # Ordinals
            'primeiro', 'primeira', 'segundo', 'segunda', 'terceiro', 'terceira',
            'quarto', 'quarta', 'quinto', 'quinta', 'sexto', 'sexta',
            'sétimo', 'sétima', 'oitavo', 'oitava', 'nono', 'nona',
            'décimo', 'décima', 'vigésimo', 'trigésimo', 'vigésimo', 'vigésima',
            'trigésimo', 'trigésima', 'quadragésimo', 'quadragésima',
            'quinquagésimo', 'quinquagésima', 'sexagésimo', 'sexagésima',
            'septuagésimo', 'septuagésima', 'octogésimo', 'octogésima',
            'nonagésimo', 'nonagésima', 'centésimo', 'centésima',
            'milésimo', 'milésima',

            # Fractional
            'meio', 'meia', 'terço', 'quarto', 'quinto', 'sexto', 'sétimo',
            'oitavo', 'nono', 'décimo', 'avos',
        }

        # Compile regex patterns
        punctuation = ''.join([_punct for _punct in string.punctuation if _punct != '-'])
        self.pattern_punctuation = re.compile(r'(?u)[' + punctuation + ']')
        self.literal_number_pattern = re.compile(r'\d+')
        self.acronym_pattern = re.compile(r'[A-Z]{2,}')
        self.proper_noun_pattern = re.compile(r'^[A-Z][a-zçáàâãéèêíìîóòôõúùû]*-[A-Z][a-zçáàâãéèêíìîóòôõúùû]*')

    def strip_punctuation(self, word: str) -> str:
        return re.sub(self.pattern_punctuation, ' ', word)

    def ends_with_hyphen(self, word: str) -> bool:
        return self.strip_punctuation(word).strip().endswith('-')

    def should_preserve_hyphen(self, word: str) -> bool:
        """
        Determines if a hyphen in a Portuguese word should be preserved.
        
        Args:
            word (str): The word containing a hyphen
            
        Returns:
            bool: True if hyphen should be preserved, False if it's likely a line break
        """
        if '-' not in word:
            return False

        if is_long_word(word):
            return True

        if is_mesoclysis(word):
            return True

        # Split the word by hyphen
        parts = [part.strip() for part in self.strip_punctuation(word).split('-')]

        # Check for literal numbers
        if any(self.literal_number_pattern.search(part) for part in parts):
            return True

        # Check for acronyms (all uppercase tokens)
        if any(self.acronym_pattern.fullmatch(part) for part in parts):
            return True

        # Check for proper nouns (first letter of each part is uppercase)
        if self.proper_noun_pattern.match(word):
            return True

        # Check for oblique pronouns
        if parts[-1].lower() in self.oblique_pronouns:
            return True

        # Check for prefixes
        if parts[0].lower() in self.prefixes:
            return True

        # Check for suffixes
        if parts[-1].lower() in self.suffixes:
            return True

        # Check for kinship terms
        if any(part.lower() in self.kinship_terms for part in parts):
            return True

        # Check for number words
        if any(part.lower() in self.number_words for part in parts):
            return True

        # Additional patterns for compound words
        # Check for geographic compound patterns (common in Brazilian Portuguese)
        geographic_patterns = [
            r'.*-(açu|guaçu|mirim|mirin)$',
            r'^(nova|novo|são|santa|santo)-.*',
        ]

        for pattern in geographic_patterns:
            if re.match(pattern, word.lower()):
                return True

        # Check for compound adjectives/adverbs
        compound_patterns = [
            r'.*-mente$',  # adverbs ending in -mente
            r'.*-or$',  # comparative forms
            r'bem-.*',  # bem- compounds
            r'mal-.*',  # mal- compounds
            r'não-.*',  # não- compounds
            r'auto-.*',  # auto- compounds
            r'co-.*',  # co- compounds
            r'ex-.*',  # ex- compounds
            r'pós-.*',  # pós- compounds
            r'pré-.*',  # pré- compounds
        ]

        for pattern in compound_patterns:
            if re.match(pattern, word.lower()):
                return True

        return False


detector = PortugueseHyphenDetector()
compound_detector = PortugueseCompoundDetector()


def should_preserve_hyphen(word: str) -> bool:
    return detector.should_preserve_hyphen(word) is True or compound_detector.is_compound_adjective(
        word) is True or is_mesoclysis(word)


def remove_invalid_hyphen(sentence: str) -> str:
    result = []
    words = sentence.split()
    for idx, word in enumerate(words):
        if '-' in word:
            if idx > 0 and is_section_number(words[idx - 1]):
                result.append(word)
                continue
            if detector.should_preserve_hyphen(word) is False and compound_detector.is_compound_adjective(word) \
                    is False and not detector.ends_with_hyphen(word):
                result.append(word.replace('-', ''))
            else:
                result.append(word)
        else:
            result.append(word)
    return ' '.join(result)


def get_possible_split_words(text: str) -> List[str]:
    return [_match for _match in __HYPHEN_SPLIT_WORDS_CHECK__.findall(text)]


def get_possible_compound_spans(text: str) -> List[str]:
    return [_match for _match in __HYPHEN_COMPOUND_CHECK__.findall(text)]
