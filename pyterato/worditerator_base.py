import abc
from typing import List, Any, Tuple, Optional


class BaseWordIterator:
    def __iter__(self) -> Any:
        return self

    @abc.abstractmethod
    def __next__(self) -> Tuple[str, Optional[int]]:
        pass
