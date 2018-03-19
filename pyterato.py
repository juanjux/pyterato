#!/usr/bin/env python3

from pprint import pprint
from time import sleep

import uno
from unotools import Socket, connect
from unotools.component.writer import Writer

# Checks:
# 1. Using words finished in "-mente" more than once every two paragraphs.
# 2. Using pedantic say-words in dialogs.
# 3. Using the basic say-words "dijo" and "preguntó" too much in dialogs.
# 4. Repeating very similar words too closely.

# TODO:
# - Show the results in LibreOffice
# - Factorize the looping over old words so it's only done once for every new word
#   (checking if the index applies for every check).
# - Agregate all the reports by sections.
# - Add explanation and examples of bad/good usage for usually missused saywords.
# - Detect dialogs.
# - Detect saywords conjugations.

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

LATEST_WORDS = []

def initialize():
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
                    "com.sun.star.bridge.UnoUrlResolver", localContext )
    ctx = resolver.resolve( "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext" )
    smgr = ctx.ServiceManager
    return smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)


class WordIterator:
    def __init__(self, text):
        self.cursor = text.createTextCursor()
        self.cursor.gotoStart(False)
        self.text = text
        self.prev_words = []

    def __iter__(self):
        return self

    def __next__(self):
        self.cursor.gotoEndOfWord(True)
        word = ''.join(e for e in self.cursor.String.lower() if e.isalnum())

        self.prev_words.append(word)
        if not self.cursor.gotoNextWord(False):
            raise StopIteration
        return word


def check_mente(word, words):
    findings = []
    if word != 'mente' and word.endswith('mente'):
        for idx, oldword in enumerate(reversed(words[-check_mente.oldwords:-1])):
            if oldword != 'mente' and oldword.endswith('mente'):
                findings.append((oldword, idx))

    if findings:
        print('Repetición de palabras con sufijo -mente desde "%s":' % word)
        for f in findings:
            print('\t%s, %d palabras detrás' % f)
        print()
check_mente.oldwords = 100


def check_repetition(word, words):
    # FIXME: search for approximate words or words containing this too
    if word in COMMON_WORDS:
        return

    findings = []
    for idx, oldword in enumerate(reversed(words[-check_repetition.oldwords:-1])):
        if oldword == word:
            findings.append(idx)

    if findings:
        print('Repetición de palabras desde "%s":' % word)
        for f in findings:
            print('\t- %d palabras detrás' % f)
        print()
check_repetition.oldwords = 50


def check_contained(word, words):
    if word in COMMON_WORDS:
        return

    findings = []
    for idx, oldword in enumerate(reversed(words[-check_contained.oldwords:-1])):
        if oldword in COMMON_WORDS:
            continue

        if oldword and not oldword.endswith('mente') and oldword != word:
            if word in oldword or oldword in word:
                findings.append((oldword, idx))

    if findings:
        print('Repetición de palabras continentes desde "%s":' % word)
        for f in findings:
            print('\t- "%s", %d palabras detrás' % f)
        print()
check_contained.oldwords = 15


def check_saywords(word):
    if word in USUALLY_PEDANTIC_SAYWORDS:
        print('Verbo generalmente pedante si se usa en diálogos: ', word)

    if word in USUALLY_MISUSED_SAYWORDS:
        print('Verbo generalmente mal utilizado en diálogos: ', word)


ENABLED_CHECKS = (check_mente, check_repetition)

def main():
    desktop = initialize()
    model = desktop.getCurrentComponent()
    text = model.Text
    words = WordIterator(text)

    for word in words:
        if not word:
            continue

        check_mente(word, words.prev_words)
        check_repetition(word, words.prev_words)
        check_contained(word, words.prev_words)
        check_saywords(word)

if __name__ == '__main__':
    main()
