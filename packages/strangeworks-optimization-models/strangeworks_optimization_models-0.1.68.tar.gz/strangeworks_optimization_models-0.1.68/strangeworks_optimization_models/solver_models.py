import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class StrangeworksSolverType(Enum):
    ProviderSolver = "ProviderSolver"


class StrangeworksSolver(ABC):
    solver: Any
    solver_type: StrangeworksSolverType
    solver_options: dict | None = None
    strangeworks_parameters: dict | None = None

    @abstractmethod
    def to_str(self) -> str: ...

    @abstractmethod
    def from_str(self) -> str: ...


class StrangeworksProviderSolver(StrangeworksSolver):
    def __init__(
        self,
        provider: str,
        solver: str,
    ):
        self.provider = provider
        self.solver = solver
        self.solver_type = StrangeworksSolverType.ProviderSolver

    def to_str(self) -> str:
        return f"{self.provider}.{self.solver}"

    def to_dict(self) -> dict:
        return {
            "solver": f"{self.provider}.{self.solver}",
            "solver_type": self.solver_type,
            "solver_options": json.dumps(self.solver_options) if self.solver_options else None,
            "strangeworks_parameters": json.dumps(self.strangeworks_parameters) if self.solver_options else None,
        }

    @staticmethod
    def from_str(solver_str, solver_options=None):
        provider, solver = solver_str.split(".", 1)
        p = StrangeworksProviderSolver(provider=provider, solver=solver)
        p.solver_options = json.loads(solver_options) if solver_options else None
        return p


class StrangeworksSolverFactory:
    @staticmethod
    def from_solver(solver: StrangeworksSolver | str | None):
        if solver is None:
            return None
        elif isinstance(solver, StrangeworksSolver):
            return solver
        elif isinstance(solver, str):
            return StrangeworksProviderSolver.from_str(solver)
        else:
            raise ValueError("Unsupported solver type")

    @staticmethod
    def from_solver_str(
        solver_str: str,
        solver_type: str | None = None,
        solver_options: str | None = None,
        strangeworks_parameters: str | None = None,
    ):
        if solver_type not in ["ProviderSolver", None]:
            raise ValueError("Unsupported solver type")

        if solver_type == "ProviderSolver" or solver_type is None:
            if len(solver_str.split(".", 1)) != 2:
                raise ValueError("Unprocessable solver string. Solver string must be in the format provider.solver")

            p = StrangeworksProviderSolver.from_str(solver_str, solver_options)
            p.strangeworks_parameters = json.loads(strangeworks_parameters) if strangeworks_parameters else None
            return p
