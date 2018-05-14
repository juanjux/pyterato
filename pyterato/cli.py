#!/usr/bin/env python3

import abc
import os
from fnmatch import fnmatch
from pprint import pprint
from collections import OrderedDict

# XXX move to where needed
from pyterato.worditerator_lo import LibreOfficeWordIterator
from pyterato.worditerator_txtfile import TxtFileWordIterator
import pyterato.checks as checks

# TODO:
# - Show the results in LibreOffice
# - Factorize the looping over old words so it's only done once for every new word
#   (checking if the index applies for every check).
# - Add explanation and examples of bad/good usage for usually missused saywords.
# - Detect dialogs for the saywords checker.
# - Detect saywords conjugations.
# - Check contained: normalize accents
# - Check: intransitive verbs used as transitive (tamborilear).
# - See if there is any way to optimize the word by word iteration while keeping the
#   page number (the current method it's pretty slow on the LibreOffice side).
# - Way to disable or enable checks individually using command line parameters or a
#   config file.
# - MyPy typing.


def print_results(findings):
    total = 0
    for page in findings:
        if page is not None:
            print('Página %d: ' % page)

        flist = findings[page]
        for typefindings in flist:
            for f in typefindings:
                total += 1
                print(f)

        print(checks.SEPARATOR + os.linesep)
        print('Total: %d avisos emitidos' % total)


def main():
    # words = LibreOfficeWordIterator(paging=False)
    words = TxtFileWordIterator('/home/juanjux/cap1.txt')
    findings = OrderedDict()

    for word, page in words:
        if not word or word in checks.COMMON_WORDS:
            continue

        tmpfindings = []

        if page not in findings:
            findings[page] = []

        for cls in checks.all_checks:
            tmpfindings.append(cls.check(word, words.prev_words))

        # print(tmpfindings)
        for f in tmpfindings:
            if len(f):
                findings[page].append(f)

    print_results(findings)


if __name__ == '__main__':
    main()
