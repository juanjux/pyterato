import abc
from typing import List, Any, Tuple, Optional


class BaseWordIterator:
    def __init__(self) -> None:
        self._prev_words: List[str] = []

    def __iter__(self) -> Any:
        return self

    @abc.abstractmethod
    def __next__(self) -> Tuple[str, Optional[int]]:
        pass

    @property
    def prev_words(self) -> List[str]:
        return self._prev_words
