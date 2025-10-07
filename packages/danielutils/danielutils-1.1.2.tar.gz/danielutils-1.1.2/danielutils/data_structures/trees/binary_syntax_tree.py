from typing import Union, Any, Callable,Dict as Dict
from .binary_tree import BinaryTree
from ..graph import BinaryNode
from ...reflection import get_python_version
if get_python_version()>=(3,9):
    from builtins import dict as Dict

class BinarySyntaxTree(BinaryTree):
    """
    Binary tree data structure to represent syntax of expressions
    """

    @staticmethod
    def _evaluate_node(v: BinaryNode, operator_func_dict: Dict[Any, Callable[[Any, Any], Any]]):
        if not isinstance(v, BinaryNode) or v.left is None and v.right is None:
            return v

        lres = BinarySyntaxTree._evaluate_node(v.left, operator_func_dict)
        rres = BinarySyntaxTree._evaluate_node(v.right, operator_func_dict)

        return operator_func_dict[v.data](lres, rres)

    @property
    def bottom_right(self) -> BinaryNode:
        cur = self.root
        while hasattr(cur, "right"):
            if isinstance(cur, BinaryNode):
                if cur.right is None:
                    return cur
                cur = cur.right
            else:
                break
        return cur

    @bottom_right.setter
    def bottom_right(self, v: BinaryNode) -> None:
        cur = self.root
        while (
                hasattr(cur, "right") and
                isinstance(cur.right, BinaryNode) and
                hasattr(cur.right, "right") and
                isinstance(cur.right.right, BinaryNode)
        ):
            cur = cur.right
        cur.right = v

    @property
    def bottom_left(self) -> BinaryNode:
        cur = self.root
        while hasattr(cur, "left"):
            if isinstance(cur, BinaryNode):
                if cur.left is None:
                    return cur
                cur = cur.left
            else:
                break
        return cur

    @bottom_left.setter
    def bottom_left(self, v: BinaryNode) -> None:
        cur = self.root
        while (
                hasattr(cur, "left") and
                isinstance(cur.left, BinaryNode) and
                hasattr(cur.left, "left") and
                isinstance(cur.left.left, BinaryNode)
        ):
            cur = cur.left
        cur.left = v

    def reverse(self) -> "BinarySyntaxTree":
        return BinarySyntaxTree(self.root.reverse())

    def __reversed__(self) -> "BinarySyntaxTree":
        return self.reverse()

    def evaluate(self, operator_func_dict: Dict[Any, Callable[[Any, Any], Any]]) -> Any:
        return BinarySyntaxTree._evaluate_node(self.root, operator_func_dict)



__all__ = [
    "BinarySyntaxTree"
]
