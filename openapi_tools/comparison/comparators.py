from dataclasses import dataclass

from openapi_parser.specification import Operation, Specification

from .registry import BaseComparator, register
from .reports import ProblemReport


@dataclass
class OperationIDsProblem(ProblemReport):
    operation_ids: list[str]

    def render(self) -> str:
        sorted_op_ids = sorted(self.operation_ids)
        op_id_list = "\n".join([f"- {op_id}" for op_id in sorted_op_ids])
        return f"{self.message}\n{op_id_list}"


@register
class OperationIDsComparator(BaseComparator):
    target_type = Specification

    @staticmethod
    def _get_spec_operations(spec: Specification) -> dict[str, Operation]:
        # https://swagger.io/specification/#operation-object
        #
        # Unique string used to identify the operation. The id MUST be unique among all
        # operations described in the API. The operationId value is case-sensitive.
        #
        # -> we can use the operation ID as key (and it is a required/fixed field).
        operations = {
            str(operation.operation_id): operation
            for path in spec.paths
            for operation in path.operations
        }
        return operations

    @classmethod
    def compare(cls, spec1: Specification, spec2: Specification) -> list[ProblemReport]:
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
        # TODO: take path parameters into account

        return problems
