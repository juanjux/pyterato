#!/usr/bin/env python3

import argparse
import os
import sys
from collections import OrderedDict
from typing import Iterable, List, Optional

import pyterato_native as native

# TODO:
# - Show the results in LibreOffice
# - Add explanation and suggest replacements.
# - Detect dialog markers (--) for the saywords checker.
# - Detect verb conjugations.
# - Check: intransitive verbs used as transitive (tamborilear).
# - See if there is any way to optimize the word by word iteration while keeping the
#   page number (the current method it's super slow on the LibreOffice side).

SEPARATOR = '-' * 20

def print_results(findings) -> None:
    total = 0
    for page in findings:
        if page is not None:
            print(os.linesep + '===> Página %d: ' % page + os.linesep)

        flist = findings[page]
        for typefindings in flist:
            if type(typefindings) == str:
                total += 1
                print(typefindings)
                pass
            else:
                for f in typefindings:
                    total += 1
                    print(f)

    print(SEPARATOR + os.linesep)
    print('Total: %d avisos emitidos' % total)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    # FIXME: option to list checks
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
            '-d', '--disable',
            type=str,
            help='Desactivar tests específicos (separados por comas).'
    )
    parser.add_argument(
            '-e', '--enable',
            type=str,
            help='Activar solo tests especificos (separados por comas).'
    )
    parser.add_argument(
            'file',
            type=str,
            nargs='?',
            help='Fichero fuente de entrada (no se necesita con --libreoffice). ' +
                 'Si no se indica se usará stdin.'
    )

    args = parser.parse_args()
    if not args.txt and not args.libreoffice:
        args.txt = True

    # FIXME: unittest this!
    if args.disable and args.enable:
        print('--disable y --enable no pueden activarse a a la vez')
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

PROFILE = False

def main() -> int:
    if PROFILE:
        import cProfile
        pr = cProfile.Profile()
        pr.enable()

    options = parse_arguments()

    disable_list = set([i.strip() for i in options.disable.split(',')]) if options.disable else set()
    enable_list = set([i.strip() for i in options.enable.split(',')]) if options.enable else set()

    if options.libreoffice:
        from pyterato.worditerator_lo import LibreOfficeWordIterator
        words = LibreOfficeWordIterator(paging=options.lo_paging)  # type: ignore
    else:
        words = native.TxtFileWordIterator()  # type: ignore
        words.loadFile(options.file)  # type: ignore

    findings: OrderedDict[Optional[int], List[object]] = OrderedDict()

    checker = native.Checker()

    for dis in disable_list:
        checker.disable_check(dis)

    for en in enable_list:
        checker.enable_check(en)

    for word, page in words:  # type: ignore
        if not word:
            continue

        res_native = checker.run_checks(word)
        if len(res_native) and page not in findings:
                findings[page] = []

        for rn in res_native:
            findings[page].append(rn)

    print_results(findings)

    if PROFILE:
        import pstats, io

        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('time')
        ps.print_stats()
        print(s.getvalue())

    return 0


if __name__ == '__main__':
    main()
