#!/usr/bin/env python3

from fnmatch import fnmatch
from pprint import pprint
from collections import OrderedDict

import uno
from unotools import Socket, connect
from unotools.component.writer import Writer

import pyterato.checks as checks

# TODO:
# - Unittests!!!
# - Show the results in LibreOffice
# - Factorize the looping over old words so it's only done once for every new word
#   (checking if the index applies for every check).
# - Add explanation and examples of bad/good usage for usually missused saywords.
# - Detect dialogs for the saywords checker.
# - Detect saywords conjugations.
# - Run the checks from a list.
# - Check contained: normalize accents
# - Check: intransitive verbs used as transitive (tamborilear).
# - See if there is any way to optimize the word by word iteration while keeping the
#   page number (the current method it's pretty slow on the LibreOffice side).
# - Way to disable or enable checks individually

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
        # FIXME: this line takes most of the time!
        self.view_cursor.gotoRange(self.cursor, False)
        page = self.view_cursor.getPage()
        word = ''.join(e for e in self.cursor.String.lower() if e.isalnum())

        self.prev_words.append(word)
        if not self.cursor.gotoNextWord(False):
            raise StopIteration
        return word, page

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
        if not word or word in checks.COMMON_WORDS:
            continue

        tmpfindings = []

        if page not in findings:
            findings[page] = []

        tmpfindings.append(checks.check_mente(word, words.prev_words))
        tmpfindings.append(checks.check_repetition(word, words.prev_words))
        tmpfindings.append(checks.check_contained(word, words.prev_words))
        tmpfindings.append(checks.check_saywords(word))
        tmpfindings.append(checks.check_verbs(word))
        tmpfindings.append(checks.check_expressions(word, words.prev_words))

        for f in tmpfindings:
            if len(f):
                findings[page].append(f)

    print_results(findings)

if __name__ == '__main__':
    main()
