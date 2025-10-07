from fractions import Fraction
from typing import Union
from math import e, factorial

from .discrete import DiscreteConditionalVariable
from ...supp import FrangeSupp
from ...operator import Operator
from .....better_builtins import frange
from ...protocols import ExpectedValueCalculable, VariableCalculable


class Poisson(DiscreteConditionalVariable, ExpectedValueCalculable, VariableCalculable):
    def __init__(self, p: Union[float, Fraction]):
        super().__init__(p, FrangeSupp(frange(1, float("inf"))))

    def evaluate(self, n: int, op: Operator) -> Fraction:
        if n < 0:
            return Fraction(0, 1)
        if op == Operator.EQ:
            return Fraction((e ** (-self.p)) * (self.p ** n), factorial(n))  # type:ignore

        assert False  # TODO
        return 1 - self.evaluate(n, op.inverse)  # type:ignore

    def expected_value(self) -> Fraction:
        return self.p

    def variance(self) -> Fraction:
        return self.p


__all__ = ['Poisson']
