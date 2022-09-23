from dataclasses import dataclass, field
from itertools import chain

from openapi_parser.specification import Operation, Path, Specification

from .registry import BaseComparator, register
from .reports import ProblemReport


@register
class VersionComparator(BaseComparator):
    target_type = Specification

    @staticmethod
    def compare(spec1: Specification, spec2: Specification) -> list[ProblemReport]:
        if (version1 := spec1.info.version) == (version2 := spec2.info.version):
            return []
        return [
            ProblemReport(
                message=f"Version '{version1}' is different from '{version2}'"
            )
        ]


@dataclass
class OperationIDsProblem(ProblemReport):
    operation_ids: list[str]

    def render(self) -> str:
        sorted_op_ids = sorted(self.operation_ids)
        op_id_list = "\n".join([f"- {op_id}" for op_id in sorted_op_ids])
        return f"{self.message}\n{op_id_list}"


@dataclass
class PathMatch:
    paths: list[Path]


@dataclass
class PathMatcher:
    paths1: list[Path]
    paths2: list[Path]
    _matches: list[PathMatch] = field(init=False, default_factory=list)
    _matches_calculated = False

    def __post_init__(self):
        self._paths1 = self._preprocess_paths(self.paths1)
        self._paths2 = self._preprocess_paths(self.paths2)

    def _preprocess_paths(self, paths: list[Path]):
        # order by length, longest first -> this should yield the most specific matches
        sorted_paths = sorted(paths, key=lambda path: len(path.url), reverse=True)
        return {path.url: path for path in sorted_paths}

    def get_matches(self) -> list[PathMatch]:
        """
        Iterate over one collection of paths, popping matches from both collections.

        By iterating over every path in the first collection, we extract all the
        possible matches. By popping results from the pre-processing datastructures, we
        maintain a collection of unmatched paths in either collection of paths.
        """
        path_urls1 = list(self._paths1.keys())
        path1_prefix = ""
        path2_prefix = ""
        for path1_url in path_urls1:
            match_found, path2_url = False, ""

            # exact matches always get priority
            if path1_url in self._paths2:
                path2_url = path1_url
                continue

            # check if set of paths 2 has a prefix relative to set of paths 1
            for path2_url in list(self._paths2.keys()):
                if path2_url.endswith(path1_url):
                    path2_prefix = path2_url.removesuffix(path1_url)
                    match_found = True
                    break
                elif path1_url.endswith(path2_url):
                    path1_prefix = path1_url.removesuffix(path2_url)
                    match_found = True
                    break

            if match_found:
                path1 = self._paths1.pop(path1_url)
                path2 = self._paths2.pop(path2_url)
                match = PathMatch(paths=[path1, path2])
                self._matches.append(match)
                continue

        self._matches_calculated = True
        return self._matches

    @property
    def has_unmatched_paths(self):
        if not self._matches_calculated:
            self.get_matches()
        return any(*self._paths1.keys(), *self._paths2.keys())

    def get_mismatch_reports(self) -> list[ProblemReport]:
        problems = []
        paths = (
            ("spec 2", self._paths1.keys()),
            ("spec 1", self._paths2.keys()),
        )
        for spec_label, path_keys in paths:
            for path in path_keys:
                problems.append(
                    ProblemReport(
                        message=f"The path '{path}' is not present in {spec_label}"
                    )
                )
        return problems


@register
class OperationsComparator(BaseComparator):
    target_type = Specification

    @staticmethod
    def _get_operation_id(url: str, operation: Operation) -> str:
        if operation.operation_id:
            return operation.operation_id
        # skip the leading slash, which is REQUIRED by the API spec
        bits = (
            ["_openapi_tools_generated"] + url[1:].split("/") + [operation.method.value]
        )
        return "_".join(bits)

    @classmethod
    def compare(cls, spec1: Specification, spec2: Specification) -> list[ProblemReport]:
        problems = []
        # search the paths by suffix match
        matcher = PathMatcher(spec1.paths, spec2.paths)
        pairs = matcher.get_matches()
        if matcher.has_unmatched_paths:
            problems += matcher.get_mismatch_reports()

        for pair in pairs:
            problems += register.compare(*pair.paths)

        # run comparison for nested operations
        # TODO: take path parameters into account, as openapi-parser DOES not do this
        # Possibly override via builder?

        return problems
