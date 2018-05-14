import abc

class BaseWordIterator:
    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self):
        pass
