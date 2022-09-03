"""
Compare OpenAPI specs for equivalency.
"""
from .parser import parse


def compare(uri1: str, uri2: str):
    spec1 = parse(uri1)
    spec2 = parse(uri2)
    import bpdb

    bpdb.set_trace()
