from typing import Callable, Any, Union, TypeVar
from ..heap import Heap
from ..comparer import Comparer, CompareGreater
from ..functions import default_weight_function
from .queue import Queue

T = TypeVar("T")


class PriorityQueue(Queue[T]):
    """
    A priority queue implementation based on a binary heap.

    Args:
        weight_func (Callable[[T], Union[int, float]], optional): A function to calculate the weight of items added
            to the queue. Defaults to default_weight_function.
        comparer (Comparer, optional): The comparer to use when comparing weights of items in the queue.
            Defaults to Comparer.GREATER.

    Raises:
        ValueError: Raised if an item with the same weight value is added more than once.

    Methods:
        pop() -> T:
            Removes and returns the item with the highest priority (i.e., the lowest weight value) from the queue.
        push(value: T):
            Adds a new item to the queue with the specified value and weight.
        peek() -> T:
            Returns the item with the highest priority
            (i.e., the lowest weight value) from the queue without removing it.
        __str__() -> str:
            Returns a string representation of the queue.

    Example:
        >>> pq = PriorityQueue()
        >>> pq.push(5)
        >>> pq.push(10)
        >>> pq.push(3)
        >>> pq.pop()
        10
    """

    def __init__(self, weight_func: Callable[[Any], Union[int, float]] = default_weight_function):
        super().__init__()
        comparer = CompareGreater if weight_func is default_weight_function else Comparer(  # type:ignore
            lambda a, b: weight_func(a) - weight_func(b))  # type:ignore
        self.data: Heap = Heap(comparer)  # type:ignore
        self.weight_func = weight_func
        self.dct: dict = {}

    def pop(self) -> T:
        """
        Removes and returns the item with the highest priority (i.e., the lowest weight value) from the queue.

        Returns:
            T: The item with the highest priority in the queue.

        Raises:
            KeyError: Raised if the queue is empty.
        """
        item_weight = self.data.pop()
        res = self.dct[item_weight]
        del self.dct[item_weight]
        return res

    def push(self, value: T) -> None:
        """
        Adds a new item to the queue with the specified value and weight.

        Args:
            value (T): The value of the item to add to the queue.

        Returns:
            None

        Raises:
            ValueError: Raised if an item with the same weight value is added more than once.
        """
        item_weight = self.weight_func(value)
        if item_weight in self.dct:
            raise ValueError(
                "Can't have same weight value more than once in current implementation")
        self.data.push(item_weight)
        self.dct[item_weight] = value

    def peek(self) -> T:
        """
        Returns the item with the highest priority (i.e., the lowest weight value) from the queue without removing it.

        Returns:
            T: The item with the highest priority in the queue.

        Raises:
            KeyError: Raised if the queue is empty.
        """
        return self.dct[self.data.peek()]

    def __str__(self) -> str:
        """
        Returns a string representation of the queue.

        Returns:
            str: A string representation of the queue.
        """
        return str([str(self.dct[w]) for w in [self.data[i] for i in range(len(self.data))]])


__all__ = [
    "PriorityQueue"
]
