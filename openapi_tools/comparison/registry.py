"""
Registry for comparators.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .reports import ProblemReport


@dataclass
class BaseComparator:
    input1: Any
    input2: Any
    # class attribute
    target_type: type = field(init=False)

    def run_comparison(self) -> list[ProblemReport]:
        results = self.compare(self.input1, self.input2)
        return results

    @classmethod
    def compare(cls, input1: Any, input2: Any) -> list[ProblemReport]:
        raise NotImplementedError


class Registry:
    def __init__(self):
        self._register = defaultdict(list)

    def __call__(self, comparator: type[BaseComparator]):
        self._register[comparator.target_type].append(comparator)

    def compare(self, input1: Any, input2: Any) -> list[ProblemReport]:
        assert type(input1) == type(input2), "Can't compare different types"
        target_type = type(input1)
        problems = []
        for cls in self._register[target_type]:
            comparator = cls(input1, input2)
            problems += comparator.run_comparison()
        return problems


register = Registry()
