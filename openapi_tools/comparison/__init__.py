"""
Compare OpenAPI specs for equivalency.
"""
from ..parser import parse
from . import comparators  # NOQA - registering the comparators
from .registry import register


def compare(uri1: str, uri2: str):
    spec1 = parse(uri1)
    spec2 = parse(uri2)
    problems = register.compare(spec1, spec2)

    if not problems:
        print("API specs are functionaly equivalent!")
        return

    for problem in problems:
        print(problem.render())
