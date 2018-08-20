import sys
from typing import Tuple, Optional

from pyterato.worditerator_base import BaseWordIterator


class TxtFileWordIterator(BaseWordIterator):
    # FIXME: read by line, maybe using the file own (line) iterator
    def __init__(self, fname: str) -> None:
        super().__init__()

        self.words_idx = 0

        if not fname:
            print('Leyendo de entrada estándar...')
            self.text = sys.stdin.read()
        else:
            with open(fname, 'r') as f:
                self.text = f.read()

        self.words = self.text.split()

    def __next__(self) -> Tuple[str, Optional[int]]:
        try:
            ret = self.words[self.words_idx]
        except IndexError:
            raise StopIteration

        ret = ''.join(list(filter(lambda x: x.isalnum(), ret)))
        self.words_idx += 1
        return ret, None
