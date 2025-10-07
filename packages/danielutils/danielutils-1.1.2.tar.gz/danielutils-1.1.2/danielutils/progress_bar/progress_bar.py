import logging
import math
import time
from abc import ABC, abstractmethod
from typing import Optional, Type, List, Iterable, Any
from ..logging_.utils import get_logger

try:
    from tqdm import tqdm
except ImportError:
    from ..mock_ import MockImportObject

    tqdm = MockImportObject("`tqdm` is not installed")  # type:ignore

logger = get_logger(__name__)


class ProgressBar(ABC):
    """An interface

    Args:
        ABC (_type_): _description_
    """
    DEFAULT_BAR_FORMAT = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}"

    @abstractmethod
    def __init__(self, total, position: int, unit="it", bar_format: str = DEFAULT_BAR_FORMAT, *, desc: str,
                 **kwargs) -> None:
        self.desc: str = desc
        self.total = total
        self.position = position
        self.unit = unit
        self.bar_format = bar_format
        self.writes: List[str] = []
        logger.info("ProgressBar initialized: %s (total=%s, position=%s, unit=%s)", desc, total, position, unit)

    @property
    def num_writes(self):
        return len(self.writes)

    @abstractmethod
    def update(self, amount: float = 1, **kwargs) -> None:
        """A function to update the progress-bar's value by a positive relative amount
        """

    @abstractmethod
    def _write(self, *args: str, sep: str = " ", end: str = "\n") -> None: ...

    def write(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        """A function to write additional text with the progress bar
        """
        processed = list(map(str, args))
        message = sep.join(processed) + end
        self._write(*processed, sep=sep, end=end)
        self.writes.append(message)

    @abstractmethod
    def reset(self) -> None:
        """A function to reset the progress-bar's progress
       """

    @abstractmethod
    def __iter__(self): ...


try:
    from tqdm import tqdm

    ProgressBar.register(tqdm)
except ImportError:
    pass

__all__ = [
    'ProgressBar',
]
