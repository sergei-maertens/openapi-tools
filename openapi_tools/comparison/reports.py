from dataclasses import dataclass


@dataclass
class ProblemReport:
    message: str

    def render(self) -> str:
        return self.message
