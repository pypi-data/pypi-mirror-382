import logging
from typing import Iterable, get_args, Union, Set as Set
from ..reflection import get_python_version
from ..logging_.utils import get_logger

logger = get_logger(__name__)

if get_python_version() >= (3, 9):
    from builtins import set as Set


def to_set(x: Union[type, Iterable[type]]) -> Set[int]:
    """converts type/types to a set representing them
    """
    logger.debug("Converting type to set: %s", x)
    res: Set[int] = set()
    if hasattr(x, "__origin__") and x.__origin__ is Union:
        logger.debug("Processing Union type")
        for xi in get_args(x):
            res.update(to_set(xi))
    elif isinstance(x, Iterable):
        logger.debug("Processing Iterable type")
        for v in x:
            res.update(to_set(v))
        return res
    else:
        logger.debug("Adding single type ID: %s", id(x))
        res.update(set([id(x)]))
    logger.debug("Result set: %s", res)
    return res


def types_subseteq(a: Union[type, Iterable[type]], b: Union[type, Iterable[type]]) -> bool:
    """checks if 'a' is contained in 'b' typing wise

    Args:
        a (type | Iterable[type])
        b (type | Iterable[type])

    Returns:
        bool: result of containment
    """
    logger.debug("Checking type subset: %s ⊆ %s", a, b)
    result = to_set(a).issubset(to_set(b))
    logger.debug("Type subset result: %s", result)
    return result


__all__ = [
    "types_subseteq"
]
