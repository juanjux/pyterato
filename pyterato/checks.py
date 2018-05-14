import abc
from fnmatch import fnmatch
from typing import List, Set, Tuple, Union, TypeVar, Generic, Any


COMMON_WORDS: Set[str] = {
        "el", "él", "lo", "la", "le", "los", "las", "que", "qué", "cual", "cuál",
        "cuales", "como", "cómo", "este", "éste", "esta", "ésta", "ese", "esa", "eso",
        "esos", "aquel", "aquello", "aquella", "y", "o", "ha", "han", "con", "sin",
        "desde", "ya", "aquellos", "aquellas", "se", "de", "un", "uno", "unos", "una",
        "unas", "con", "ante", "ya", "para", "sin", "mas", "más",
        "serían", "sería", "en", "por", "mi", "mis", "si", "sí", "no", "hasta", "su",
        "mi", "sus", "tus", "sobre", "del", "a", "e", "pero", "había", "habías", "habían",
        "habría", "habrías",  "habrían", "ser", "al", "sido", "haya", "otra", "me", "te",
        "dijo", "dije", "preguntó", "pregunté", "ni", "les", "hecho",

        # verbo ser is never considered repetitive except for some uncommon/longer conjugations
        "sea", "sean", "soy", "eres", "es", "somos", "sois", "son", "era", "eras",
        "érais", "eran", "seré", "serás", "será", "seréis", "serán", "sido",
        "sería", "serías", "seríamos", "seríais", "serían", "fui", "fuiste", "fue",
        "fuimos", "fueron", "sé", "sed", "sean", "fuera",
        "fueras", "fuera", "fuese", "fueses", "fuesen", "siendo",
}

# First element is the root and others are non verbal words (thus allowed)
# FIXME: check the sufix for verbal conjugations
USUALLY_MISUSED_VERB_ROOTS: List[Tuple[str, ...]] = [
        ("espet", "espeto", "espetos"),
        ("mascull",),
        ("perl", "perla", "perlas"),
        ("empalid",),
        ("tinti",),
        ("manten", "mantenido", "mantenida", "mantenidos", "mantenidas"),
        ("mantuv",),
        ("tamboril", "tamborilero", "tamborilera", "tamborileros", "tamborileras"),
]

# Words too frecuently used that usually have lots of more proper synonymous
OVERUSED_WORDS: Set[str] = {
        "sonido*", "ruido*", "cosa*", "provoc*", "usar", "usó", "usamos",
        "usab*", "usáb", "usas*", "usar*", "usad*", "emplea*",
}

# Ditto. On a separate list to apply the conjugation detector once if it's implemented
OVERUSED_VERBS: Set[str] = {
        "provoc*", "usar", "usó", "usamos", "usab*", "usáb", "usas*",
        "usar*", "usad*", "emplea*",
}
_OVERUSED_ALL = OVERUSED_WORDS.union(OVERUSED_VERBS)

USUALLY_PEDANTIC_SAYWORDS: Set[str] = {
        "rebuznó", "rugió", "rugí", "bramó", "bramé", "declaró", "declaré",
        "inquirió", "inquirí", "sostuvo", "sostuve", "refirió", "referí",
        "aseveró", "aseveré", "arguyó", "argüí",
}

USUALLY_MISUSED_SAYWORDS: Set[str] = {
        "comentó", "comenté", "interrogó", "interrogué", "amenazó", "amenacé",
        "conminó", "conminé", "exhortó", "exhorté", "aludió", "aludí",
}

# These are in reverse order. Last word can't use a pattern.
USUALLY_MISUSED_EXPRESSIONS: List[List[str]] = [
        ["sacud*", "la", "cabeza"],
        ["perlab*", "*", "frente"],
        ["provoc*", "*", "polémica"],
        # usually obvious from the context/anglicism:
        ["qued*", "de", "pie"], ["qued*", "sentad*"],
        ["esta*", "de", "pie"], ["esta*", "sentad*"],
        ["encontr*", "de", "pie"], ["encontr*", "sentad*"],
]
for i in USUALLY_MISUSED_EXPRESSIONS:
    i.reverse()

# To optimize lookups of new potential expressions:
_USUALLY_MISUSED_EXPRESSIONS_LAST_WORDS = set()
for exp in USUALLY_MISUSED_EXPRESSIONS:
    _USUALLY_MISUSED_EXPRESSIONS_LAST_WORDS.add(exp[0])


class BaseFind(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def check(word: str, words: List[str]) -> List[Any]:
        pass

    def __init__(self, word: str) -> None:
        self.word = word

    @abc.abstractmethod
    def get_message(self) -> str:
        pass

    def __str__(self) -> str:
        return self.get_message()


class OverUsedFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        for overused in _OVERUSED_ALL:
            if fnmatch(word, overused):
                return [OverUsedFind(word)]
        return []

    def get_message(self) -> str:
        return 'Palabras/verbos comodín: %s' % self.word


class MenteFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str], oldwords=100) -> List[BaseFind]:
        findings = []
        if word != 'mente' and word.endswith('mente'):
            for idx, oldword in enumerate(words[-oldwords:-1]):  # type: ignore
                if oldword != 'mente' and oldword.endswith('mente'):
                    # findings.append((oldword, idx))
                    findings.append(MenteFind(word, oldword, oldwords - idx))  # type: ignore

        return findings  # type: ignore

    def __init__(self, word: str, oldword: str, idx: int) -> None:
        super().__init__(word)
        self.oldword = oldword
        self.idx = idx

    def get_message(self) -> str:
        return 'Repetición de palabra con sufijo mente ("%s") %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)


class RepetitionFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str], oldwords=50) -> List[BaseFind]:
        # FIXME: search for approximate words or words containing this too
        findings = []
        for idx, oldword in enumerate(words[-oldwords:-1]):  # type: ignore
            if oldword == word:
                # findings.append(idx)
                findings.append(RepetitionFind(word, oldwords - idx))  # type: ignore

        return findings  # type: ignore

    def __init__(self, word: str, idx: int) -> None:
        super().__init__(word)
        self.idx = idx

    def get_message(self) -> str:
        return 'Repetición de palabra "%s" %d palabras atrás' %\
                (self.word, self.idx)


class ContainedFind(BaseFind):
    # FIXME: compare against the root of the word.
    @staticmethod
    def check(word: str, words: List[str], oldwords=15) -> List[BaseFind]:
        findings = []
        for idx, oldword in enumerate(words[-oldwords:-1]):  # type: ignore
            if oldword in COMMON_WORDS:
                continue

            if oldword and not oldword.endswith('mente') and oldword != word:
                if word in oldword or oldword in word:
                    findings.append(ContainedFind(word, oldword, idx))

        return findings  # type: ignore

    def __init__(self, word: str, oldword: str, idx: int) -> None:
        super().__init__(word)
        self.oldword = oldword
        self.idx = idx

    def get_message(self) -> str:
        return 'Repetición de palabra contenida "%s" %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)


class SayWordsFind(BaseFind):
    # FIXME: check for a "-" or the equivalent long version to check that we're
    # probably in a dialog.
    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        findings: List[object] = []

        if word in USUALLY_PEDANTIC_SAYWORDS:
            findings.append(PedanticSayFind(word))

        if word in USUALLY_MISUSED_SAYWORDS:
            findings.append(MisusedSayFind(word))

        return findings  # type: ignore

    def __init__(self, word: str) -> None:
        super().__init__(word)


class PedanticSayFind(SayWordsFind):
    def __init__(self, word: str) -> None:
        super().__init__(word)

    def get_message(self) -> str:
        return 'Verbo generalmente pedante en diálogos: %s' % self.word


class MisusedSayFind(SayWordsFind):
    def __init__(self, word: str) -> None:
        super().__init__(word)

    def get_message(self) -> str:
        return 'Verbo generalmente mal usado en diálogos: %s' % self.word


class MisusedVerbFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        for misused in USUALLY_MISUSED_VERB_ROOTS:
            root = misused[0]
            if word.startswith(root):
                for allowed in misused[1:]:
                    if word == allowed:
                        return []
                else:
                    return [MisusedVerbFind(word)]

        return []

    def __init__(self, word: str) -> None:
        super().__init__(word)

    def get_message(self) -> str:
        return 'Verbo generalmente mal usado: %s' % self.word


class MisusedExpressionFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        if word not in _USUALLY_MISUSED_EXPRESSIONS_LAST_WORDS:
            return []

        for exp in USUALLY_MISUSED_EXPRESSIONS:
            if len(exp) > len(words) + 1 or not fnmatch(word, exp[0]):
                continue

            # match, check the previous words in the expression
            prevcount = 2
            for exp_word in exp[1:]:
                if not fnmatch(words[-prevcount], exp_word):
                    break
                prevcount += 1
            else:
                # matched
                return [MisusedExpressionFind(word, exp)]

        return []

    def __init__(self, word: str, expression: List[str]) -> None:
        super().__init__(word)
        self.expression = expression

    def get_message(self) -> str:
        return 'Expression generalmente mal usada: %s' % ' '.join(reversed(self.expression))


all_checks = [OverUsedFind, MenteFind, RepetitionFind, ContainedFind, SayWordsFind,
          MisusedVerbFind, MisusedExpressionFind]
