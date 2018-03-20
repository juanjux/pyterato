#!/usr/bin/env python3

from pprint import pprint
from time import sleep
from collections import OrderedDict

import uno
from unotools import Socket, connect
from unotools.component.writer import Writer

# TODO:
# - Show the results in LibreOffice
# - Factorize the looping over old words so it's only done once for every new word
#   (checking if the index applies for every check).
# - Add explanation and examples of bad/good usage for usually missused saywords.
# - Detect dialogs, check saywords online in them.
# - Detect saywords conjugations.
# - Run the checks from a list.
# - Print page number of the findings
# - Check contained: normalize accents
# - Check: misused/abused expressions ("perlaban la frente", "sacudir la cabeza").
# - Check: commonly misused and abused verbs (detect verb roots) (espetar, mascullar,
#          perlar, empalidecer).
# - Check: intransitive verbs used as transitive (tamborilear).

COMMON_WORDS = {
        "el", "él", "lo", "la", "le", "los", "las", "que", "qué", "cual", "cuál",
        "cuales", "como", "cómo", "este", "éste", "esta", "ésta", "ese", "esa", "eso",
        "esos", "aquel", "aquello", "aquella", "y", "o", "ha", "han", "con", "sin",
        "desde", "ya", "aquellos", "aquellas", "se", "de", "un", "uno", "unos", "una",
        "unas", "con", "ante", "ya", "para", "sin", "mas", "más", "es", "era", "eran",
        "serían", "sería", "en", "por", "mi", "mis", "si", "sí", "no", "hasta", "su",
        "mi", "sus", "tus", "sobre", "del", "a", "e", "pero", "había", "habías", "habían",
        "habría", "habrías",  "habrían", "ser", "al", "sido", "haya", "otra", "me", "te",
        "dijo", "dije", "preguntó", "pregunté", # checked by saywords_checker
}

USUALLY_PEDANTIC_SAYWORDS = {
        "rebuznó", "rugió", "rugí", "bramó", "bramé", "declaró", "declaré",
        "inquirió", "inquirí", "sostuvo", "sostuve", "refirió", "referí",
        "aseveró", "aseveré", "arguyó", "argüí",
}

USUALLY_MISUSED_SAYWORDS = {
        "comentó", "comenté", "interrogó", "interrogué", "amenazó", "amenacé",
        "conminó", "conminé", "exhortó", "exhorté", "aludió", "aludí",
}

def initialize():
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
                    "com.sun.star.bridge.UnoUrlResolver", localContext )
    ctx = resolver.resolve( "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext" )
    smgr = ctx.ServiceManager
    return smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)


class WordIterator:
    def __init__(self, text, controller):
        self.text = text
        self.controller = controller
        self.cursor = text.createTextCursor()
        self.cursor.gotoStart(False)
        self.view_cursor = self.controller.getViewCursor()
        self.prev_words = []

    def __iter__(self):
        return self

    def __next__(self):
        self.cursor.gotoEndOfWord(True)
        self.view_cursor.gotoRange(self.cursor, False)
        page = self.view_cursor.getPage()
        word = ''.join(e for e in self.cursor.String.lower() if e.isalnum())

        self.prev_words.append(word)
        if not self.cursor.gotoNextWord(False):
            raise StopIteration
        return word, page

class MenteFind:
    def __init__(self, word, oldword, idx):
        self.word = word
        self.oldword = oldword
        self.idx = idx

    def __str__(self):
        return 'Repetición de palabra con sufijo mente ("%s") %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)


def check_mente(word, words):
    findings = []
    if word != 'mente' and word.endswith('mente'):
        for idx, oldword in enumerate(reversed(words[-check_mente.oldwords:-1])):
            if oldword != 'mente' and oldword.endswith('mente'):
                # findings.append((oldword, idx))
                findings.append(MenteFind(word, oldword, idx))

    return findings
check_mente.oldwords = 100

class RepetitionFind:
    def __init__(self, word, idx):
        self.word = word
        self.idx = idx

    def __str__(self):
        return 'Repetición de palabra "%s" %d palabras atrás' %\
                (self.word, self.idx)

def check_repetition(word, words):
    # FIXME: search for approximate words or words containing this too
    if word in COMMON_WORDS:
        return []

    findings = []
    for idx, oldword in enumerate(reversed(words[-check_repetition.oldwords:-1])):
        if oldword == word:
            # findings.append(idx)
            findings.append(RepetitionFind(word, idx))

    return findings
check_repetition.oldwords = 50


class ContainedFind:
    def __init__(self, word, oldword, idx):
        self.word = word
        self.oldword = oldword
        self.idx = idx

    def __str__(self):
        return 'Repetición de palabra contenida "%s" %d palabras atrás: %s' %\
                (self.word, self.idx, self.oldword)

def check_contained(word, words):
    if word in COMMON_WORDS:
        return []

    findings = []
    for idx, oldword in enumerate(reversed(words[-check_contained.oldwords:-1])):
        if oldword in COMMON_WORDS:
            continue

        if oldword and not oldword.endswith('mente') and oldword != word:
            if word in oldword or oldword in word:
                findings.append(ContainedFind(word, oldword, idx))

    return findings
check_contained.oldwords = 15


class PedanticSayFind:
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return 'Verbo generalmente pedante en diálogos: %s' % self.word

class MisusedSayFind:
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return 'Verbo generalmente mal usado en diálogos: %s' % self.word

def check_saywords(word):
    findings = []

    if word in USUALLY_PEDANTIC_SAYWORDS:
        # findings.append(word)
        findings.append(PedanticSayFind(word))
        # print('Verbo generalmente pedante si se usa en diálogos: ', word)

    if word in USUALLY_MISUSED_SAYWORDS:
        findings.append(MisusedSayFind(word))
        # findings.append(word)
        # print('Verbo generalmente mal utilizado en diálogos: ', word)

    return findings

def print_results(findings):
    for page in findings:
        print('Página %d: ' % page)
        flist = findings[page]
        for typefindings in flist:
            for f in typefindings:
                print(f)

        print()


def main():
    desktop = initialize()
    model = desktop.getCurrentComponent()
    text = model.Text
    controller = model.getCurrentController()
    words = WordIterator(text, controller)
    findings = OrderedDict()

    for word, page in words:
        tmpfindings = []
        if not word:
            continue

        if page not in findings:
            findings[page] = []

        tmpfindings.append(check_mente(word, words.prev_words))
        tmpfindings.append(check_repetition(word, words.prev_words))
        tmpfindings.append(check_contained(word, words.prev_words))
        tmpfindings.append(check_saywords(word))

        for f in tmpfindings:
            if len(f):
                findings[page].append(f)

    print_results(findings)

if __name__ == '__main__':
    main()
