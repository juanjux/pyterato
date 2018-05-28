import abc
import os
from fnmatch import fnmatch
from typing import List, Set, Tuple, Any


COMMON_WORDS: Set[str] = {
        "el", "él", "lo", "la", "le", "los", "las", "que", "qué", "cual", "cuál",
        "cuales", "como", "cómo", "este", "éste", "esta", "esto", "ésta", "ese", "esa", "eso",
        "esos", "aquel", "aquello", "aquella", "y", "o", "ha", "han", "con", "sin",
        "desde", "ya", "aquellos", "aquellas", "se", "de", "un", "uno", "unos", "una",
        "unas", "con", "ante", "ya", "para", "sin", "mas", "más", "habeis",
        "serían", "sería", "en", "por", "mi", "mis", "si", "sí", "no", "hasta", "su",
        "mi", "sus", "tus", "sobre", "del", "a", "e", "pero", "había", "habías", "habían",
        "habría", "habrías", "habrían", "ser", "al", "sido", "haya", "otra", "me", "te",
        "dijo", "dije", "preguntó", "pregunté", "ni", "les", "hecho",
        "donde", "da", "dan", "das", "cuando", "donde", "os", "vuestros", "vuestras",
        "vosotros", "vosotras", "algo", "muy", "mas", "menos", "entre", "tras", "aún",
        "hacia",

        # verbo ser is never considered repetitive except for some uncommon/longer conjugations
        "sea", "sean", "soy", "eres", "es", "somos", "sois", "son", "era", "eras",
        "érais", "eran", "seré", "serás", "será", "seréis", "serán", "sido",
        "sería", "serías", "seríamos", "seríais", "serían", "fui", "fuiste", "fue",
        "fuimos", "fueron", "sé", "sed", "sean", "fuera", "estaba", "estaban",
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

CALCO_EXPRESSIONS: List[List[str]] = [
        ["h*", "lo", "correcto"],  # hacer lo debido, hacer el bien, etc
        ["al", "final", "del", "dia"],
        ["jug*", "*", "culo*"],  # jugarse la piel
        ["quit*", "el", "culo"],  # largate
        ["esta", "todo", "bien"],  # todo va bien
        ["esta", "todo", "correcto"],  # ditto
        ["todo", "lo", "que", "ten*", "que"],  # lo unico, solo, etc
        ["tan", "simple", "como"],  # es sencillo, en pocas palabras, en resumen...
        ["es", "donde", "pertenez*"],  # es mi casa, es mi pais, etc
        ["dame", "un", "respiro"],  # no me agobies, no me atosigues, dejame en paz
        ["condescend*"],  # desprecio (excepto cuando es "dejar hacer")
        ["suma", "decente"],  # cantidad considerable
        ["cantidad", "decente"],  # ditto
        ["devocion"],  # lealtad, afecto (solo correcto en contexto religioso)
        ["eventualmente"],  # al final, finalmente, a la larga
        ["excit*"],  # emocionado, entusiasmado, ilusionado (correcto en contexto sexual o quimico)
        ["un", "fraude"],  # farsante, impostor, tramposo
        ["interpone*", "en", "*", "camino"],  # ponerse en medio, estorbar
        ["h*", "el", "macho"],  # hacerse el duro
        ["orgullosa", "historia"],  # gloriosa historia (proud inanimado)
        ["rango"],  # graduacion (excepto en matematicas y otras ciencias)
        ["entrega", "especial"],  # entrega urgente
        ["maldicion"],  # muchas opciones...
        ["jodidamente"],  # ditto
        ["lo", "hici*s"],  # lo conseguimos (correcto en el contexto de fabricar o crear, no en el de conseguir hacer algo)
]
for i in CALCO_EXPRESSIONS:
    i.reverse()

# To optimize lookups of new potential expressions:
_USUALLY_MISUSED_EXPRESSIONS_LAST_WORDS = set()
for exp in USUALLY_MISUSED_EXPRESSIONS:
    _USUALLY_MISUSED_EXPRESSIONS_LAST_WORDS.add(exp[0])

SEPARATOR = '=' * 20


class BaseFind(abc.ABC):
    context_size = 6

    @staticmethod
    @abc.abstractmethod
    def check(word: str, words: List[str]) -> List[Any]: pass

    def __init__(self, word: str, words: List[str]) -> None:
        self.word = word
        self.context = ' '.join(words[-self.context_size:])

    @classmethod
    def code(cls) -> str:
        return cls.__name__.lower()[:-4]

    @property
    @abc.abstractmethod
    def custom_message(self) -> str: pass

    @property
    def message(self) -> str:
        return (SEPARATOR + ' [%s]' % self.code() + os.linesep +
                self.custom_message + os.linesep +
                'Contexto: ...' + self.context + '...')

    def __str__(self) -> str:
        return self.message


class OverUsedFind(BaseFind):

    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        for overused in _OVERUSED_ALL:
            if fnmatch(word, overused):
                return [OverUsedFind(word, words)]
        return []

    @property
    def custom_message(self) -> str:
        return 'Palabras/verbos comodín: %s' % self.word


class MenteFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str], oldwords=100) -> List[BaseFind]:
        findings: List[MenteFind] = []
        numprev = min(oldwords, len(words))

        if word != 'mente' and word.endswith('mente'):
            for idx, oldword in enumerate(words[-numprev:-1]):  # type: ignore
                if oldword != 'mente' and oldword.endswith('mente'):
                    findings.append(MenteFind(word, words, oldword, numprev - idx - 1))  # type: ignore

        return findings  # type: ignore

    def __init__(self, word: str, words: List[str], oldword: str, idx: int) -> None:
        super().__init__(word, words)
        self.oldword = oldword
        self.idx = idx

    @property
    def custom_message(self) -> str:
        return 'Repetición de palabra con sufijo mente ("%s") %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)


class RepetitionFind(BaseFind):
    @staticmethod
    def check(word: str, words: List[str], oldwords=50) -> List[BaseFind]:
        # FIXME: search for approximate words or words containing this too
        findings: List[RepetitionFind] = []
        numprev = min(oldwords, len(words))

        for idx, oldword in enumerate(words[-numprev:-1]):  # type: ignore
            if oldword == word:
                findings.append(RepetitionFind(word, words, numprev - idx - 1))  # type: ignore

        return findings  # type: ignore

    def __init__(self, word: str, words: List[str], idx: int) -> None:
        super().__init__(word, words)
        self.idx = idx

    @property
    def custom_message(self) -> str:
        return 'Repetición de palabra "%s" %d palabras atrás' %\
                (self.word, self.idx)


class ContainedFind(BaseFind):
    min_size = 4

    # FIXME: compare against the root of the word.
    @staticmethod
    def check(word: str, words: List[str], oldwords=15) -> List[BaseFind]:
        if len(word) < ContainedFind.min_size:
            return []

        findings: List[ContainedFind] = []
        numprev = min(oldwords, len(words))

        for idx, oldword in enumerate(words[-numprev:-1]):  # type: ignore
            if oldword in COMMON_WORDS or len(oldword) < ContainedFind.min_size:
                continue

            if oldword and not oldword.endswith('mente') and oldword != word:
                if word in oldword or oldword in word:
                    findings.append(ContainedFind(word, words, oldword, idx - 1))

        return findings  # type: ignore

    def __init__(self, word: str, words: List[str], oldword: str, idx: int) -> None:
        super().__init__(word, words)
        self.oldword = oldword
        self.idx = idx

    @property
    def custom_message(self) -> str:
        return 'Repetición de palabra contenida "%s" %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)


class SayWordsFind(BaseFind):
    # FIXME: check for a "-" or the equivalent long version to check that we're
    # probably in a dialog.
    @staticmethod
    def check(word: str, words: List[str]) -> List[BaseFind]:
        findings: List[BaseFind] = []

        if word in USUALLY_PEDANTIC_SAYWORDS:
            findings.append(PedanticSayFind(word, words))

        if word in USUALLY_MISUSED_SAYWORDS:
            findings.append(MisusedSayFind(word, words))

        return findings  # type: ignore


class PedanticSayFind(SayWordsFind):
    @property

    @classmethod
    def code(cls) -> str:
        return 'saywords'

    def custom_message(self) -> str:
        return 'Verbo generalmente pedante en diálogos: %s' % self.word


class MisusedSayFind(SayWordsFind):
    @classmethod
    def code(cls) -> str:
        return 'saywords'

    @property
    def custom_message(self) -> str:
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
                    return [MisusedVerbFind(word, words)]

        return []

    @property
    def custom_message(self) -> str:
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
                return [MisusedExpressionFind(word, words, exp)]

        return []

    def __init__(self, word: str, words: List[str], expression: List[str]) -> None:
        super().__init__(word, words)
        self.expression = expression

    @property
    def custom_message(self) -> str:
        return 'Expression generalmente mal usada: %s' % ' '.join(reversed(self.expression))


all_checks = [OverUsedFind, MenteFind, RepetitionFind, ContainedFind, SayWordsFind,
              MisusedVerbFind, MisusedExpressionFind]
