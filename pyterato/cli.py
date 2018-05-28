#!/usr/bin/env python3

import argparse
import os
from collections import OrderedDict
from typing import Iterable, List

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


def print_results(findings) -> None:
    total = 0
    for page in findings:
        if page is not None:
            print(os.linesep + '===> Página %d: ' % page + os.linesep)

        flist = findings[page]
        for typefindings in flist:
            for f in typefindings:
                total += 1
                print(f)

    print(checks.SEPARATOR + os.linesep)
    print('Total: %d avisos emitidos' % total)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
            '-t', '--txt',
            action="store_true",
            help='Usar fichero en texto plano y UTF8 como fuente de entrada (por defecto).'
    )
    group.add_argument(
            '-l', '--libreoffice',
            action='store_true',
            help='Usar Libre/Open Office como fuente de entrada.'
    )
    parser.add_argument(
            '-H', '--lo_host',
            type=str,
            default='localhost',
            help='Hostname a usar para la conexión a Libre/Open Office.'
    )
    parser.add_argument(
            '-p', '--lo_port',
            type=str,
            default='8100',
            help='Puerto a usar para la conexión a Libre/Open Office.'
    )
    parser.add_argument(
            '-P', '--lo_paging',
            action='store_true',
            help='Con --libreoffice, indicar las páginas de los errores con (lento).'
    )
    parser.add_argument(
            'file',
            nargs='?',
            type=str,
            help='Fichero fuente de entrada (no se necesita con --libreoffice). ' +
                 'Si no se indica se usará stdin.'
    )

    args = parser.parse_args()
    if not args.txt and not args.libreoffice:
        args.txt = True

    return parser.parse_args()


def main() -> int:
    options = parse_arguments()
    if options.libreoffice:
        from pyterato.worditerator_lo import LibreOfficeWordIterator
        words = LibreOfficeWordIterator(paging=options.lo_paging)  # type: ignore
    else:
        from pyterato.worditerator_txtfile import TxtFileWordIterator
        words = TxtFileWordIterator(options.file)  # type: ignore

    findings: OrderedDict[int, object] = OrderedDict()

    for word, page in words:  # type: ignore
        if not word or word in checks.COMMON_WORDS:
            continue

        tmpfindings: List[List[checks.BaseFind]] = []

        if page not in findings:
            findings[page] = []

        # call check on all classes in the check module inheriting from BaseFind
        for symname in checks.__dict__.keys():
            sym = getattr(checks, symname)
            if hasattr(sym, '__bases__') and checks.BaseFind in sym.__bases__:
                tmpfindings.append(sym.check(word, words.prev_words))  # type: ignore

        for f in tmpfindings:
            if len(f):
                findings[page].append(f)  # type: ignore

    print_results(findings)
    return 0


if __name__ == '__main__':
    main()
