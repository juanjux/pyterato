import abc

class BaseWordIterator:
    def __init__(self):
        self._prev_words = []

    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self):
        pass

    @property
    def prev_words(self):
        return self._prev_words
