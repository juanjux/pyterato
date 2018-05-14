#!/usr/bin/env python3

from fnmatch import fnmatch
from pprint import pprint
from collections import OrderedDict

import pyterato.checks as checks

# TODO:
# - Show the results in LibreOffice
# - Factorize the looping over old words so it's only done once for every new word
#   (checking if the index applies for every check).
# - Add explanation and examples of bad/good usage for usually missused saywords.
# - Detect dialogs for the saywords checker.
# - Detect saywords conjugations.
# - Once I've enough tests, normalize the check function parameters and turn them
#   into a static method of the *Find classes.
# - Run the checks from a list.
# - Check contained: normalize accents
# - Check: intransitive verbs used as transitive (tamborilear).
# - See if there is any way to optimize the word by word iteration while keeping the
#   page number (the current method it's pretty slow on the LibreOffice side).
# - Way to disable or enable checks individually using command line parameters or a
#   config file.
# - MyPy typing.


class LibreOfficeWordIterator:

    def __init__(self, paging=True):
        model, controller = self._initialize_OO()
        self.cursor = model.Text.createTextCursor()
        self.cursor.gotoStart(False)
        self.paging = paging
        if paging:
            self.view_cursor = controller.getViewCursor()
        self.prev_words = []


    def _initialize_OO(self):
        import uno

        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        ctx = resolver.resolve( "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext" )
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop", ctx)
        model = desktop.getCurrentComponent()
        return model, model.getCurrentController()


    def __iter__(self):
        return self

    def __next__(self):
        self.cursor.gotoEndOfWord(True)
        if self.paging:
            # FIXME: this line takes most of the time!
            self.view_cursor.gotoRange(self.cursor, False)
            page = self.view_cursor.getPage()
        else:
            page = None

        word = ''.join(e for e in self.cursor.String.lower() if e.isalnum())

        self.prev_words.append(word)
        if not self.cursor.gotoNextWord(False):
            raise StopIteration
        return word, page


def print_results(findings):
    for page in findings:
        if page is not None:
            print('Página %d: ' % page)

        flist = findings[page]
        for typefindings in flist:
            for f in typefindings:
                print(f)

        print()


def main():
    words = LibreOfficeWordIterator(paging=False)
    findings = OrderedDict()

    for word, page in words:
        if not word or word in checks.COMMON_WORDS:
            continue

        tmpfindings = []

        if page not in findings:
            findings[page] = []

        tmpfindings.append(checks.check_overused(word))
        tmpfindings.append(checks.check_mente(word, words.prev_words))
        tmpfindings.append(checks.check_repetition(word, words.prev_words))
        tmpfindings.append(checks.check_contained(word, words.prev_words))
        tmpfindings.append(checks.check_saywords(word))
        tmpfindings.append(checks.check_verbs(word))
        tmpfindings.append(checks.check_expressions(word, words.prev_words))

        # print(tmpfindings)
        for f in tmpfindings:
            if len(f):
                findings[page].append(f)

    print_results(findings)


if __name__ == '__main__':
    main()
