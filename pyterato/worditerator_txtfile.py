import sys
from typing import Tuple, Optional

from pyterato.worditerator_base import BaseWordIterator


class TxtFileWordIterator(BaseWordIterator):
    # FIXME: read by line, maybe using the file own (line) iterator
    def __init__(self, fname: str) -> None:
        super().__init__()

        if not fname:
            print('Leyendo de entrada estándar...')
            self.text = sys.stdin.read()
        else:
            with open(fname, 'r') as f:
                self.text = f.read()

        self.words = self.text.split()

    def __next__(self) -> Tuple[str, Optional[int]]:
        if not self.words:
            raise StopIteration

        ret = ''.join(list(filter(lambda x: x.isalnum(), self.words[0])))
        self._prev_words.append(ret)
        del self.words[0]
        return ret, None
