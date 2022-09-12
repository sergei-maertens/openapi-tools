from dataclasses import dataclass

from openapi_parser.specification import Operation, Specification

from .registry import BaseComparator, register
from .reports import ProblemReport


@register
class VersionComparator(BaseComparator):
    target_type = Specification

    @staticmethod
    def compare(spec1: Specification, spec2: Specification) -> list[ProblemReport]:
        if (version1 := spec1.info.version) == (version2 := spec2.info.version):
            return []
        return [ProblemReport(message=f"Version '{version1}' is different from '{version2}'")]


@dataclass
class OperationIDsProblem(ProblemReport):
    operation_ids: list[str]

    def render(self) -> str:
        sorted_op_ids = sorted(self.operation_ids)
        op_id_list = "\n".join([f"- {op_id}" for op_id in sorted_op_ids])
        return f"{self.message}\n{op_id_list}"


# @register
class OperationIDsComparator(BaseComparator):
    target_type = Specification

    @staticmethod
    def _get_operation_id(url: str, operation: Operation) -> str:
        if operation.operation_id:
            return operation.operation_id
        # skip the leading slash, which is REQUIRED by the API spec
        bits = ["_openapi_tools_generated"] + url[1:].split("/") + [operation.method.value]
        return "_".join(bits)

    @classmethod
    def _get_spec_operations(cls, spec: Specification) -> dict[str, Operation]:
        # https://swagger.io/specification/#operation-object
        #
        # Unique string used to identify the operation. The id MUST be unique among all
        # operations described in the API. The operationId value is case-sensitive.
        #
        # -> we can use the operation ID as key. if it's not provided (since it's an
        # optional field), we generate an ID from the path + method combination
        operations = {
            cls._get_operation_id(path.url, operation): operation
            for path in spec.paths
            for operation in path.operations
        }
        return operations

    @classmethod
    def compare(cls, spec1: Specification, spec2: Specification) -> list[ProblemReport]:
        import bpdb; bpdb.set_trace()



        spec1_operations = cls._get_spec_operations(spec1)
        spec2_operations = cls._get_spec_operations(spec2)

        spec1_op_ids = set(spec1_operations)
        spec2_op_ids = set(spec2_operations)

        # difference in operation IDs present -> find out what
        problems = []
        if spec1_op_ids != spec2_op_ids:
            if missing_in_spec1 := spec2_op_ids - spec1_op_ids:
                problems.append(
                    OperationIDsProblem(
                        message="Operation IDs mismatch - specification 1 is missing:",
                        operation_ids=list(missing_in_spec1),
                    )
                )
            if missing_in_spec2 := spec1_op_ids - spec2_op_ids:
                problems.append(
                    OperationIDsProblem(
                        message="Operation IDs mismatch - specification 2 is missing:",
                        operation_ids=list(missing_in_spec2),
                    )
                )

        # run comparison for nested operations
        # TODO: take path parameters into account, as openapi-parser DOES not do this
        # Possibly override via builder?

        return problems
