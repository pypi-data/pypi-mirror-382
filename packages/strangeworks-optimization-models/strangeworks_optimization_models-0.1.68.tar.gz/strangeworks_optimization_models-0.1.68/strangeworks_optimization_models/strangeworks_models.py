import json

from pydantic import BaseModel, ConfigDict, Field

from strangeworks_optimization_models.problem_models import StrangeworksModelFactory
from strangeworks_optimization_models.solution_models import StrangeworksSolutionFactory
from strangeworks_optimization_models.solver_models import StrangeworksSolverFactory


class StrangeworksOptimizationModel(BaseModel):
    """
    A Pydantic model for Strangeworks optimization models.

    Attributes:
        model (str): The serialized Strangeworks optimization model.
        model_type (str): The type of the Strangeworks optimization model.
        model_options (str | None): The options for the Strangeworks optimization model.
        strangeworks_parameters (str | None): The parameters for the Strangeworks optimization model.

    Methods:
        deserialize() -> StrangeworksModel:
            Builds a StrangeworksModel from a StrangeworksOptimizationModel.
        from_model(model: StrangeworksModel) -> StrangeworksOptimizationModel:
            Builds a Pydantic model from a StrangeworksModel.

    """

    model: str
    model_type: str
    model_options: str | None = None
    strangeworks_parameters: str | None = None

    model_config = ConfigDict(protected_namespaces=())

    def deserialize(self):
        """
        Builds a StrangeworksModel from a StrangeworksOptimizationModel.

        Returns:
            StrangeworksModel: The deserialized Strangeworks optimization model.
        """
        model = StrangeworksModelFactory.from_model_str(
            self.model,
            self.model_type,
            self.model_options,
            self.strangeworks_parameters,
        )
        return model

    @classmethod
    def from_model(cls, model):
        """
        Builds a Pydantic model from a StrangeworksModel.

        Args:
            model (StrangeworksModel): The Strangeworks optimization model.

        Returns:
            StrangeworksOptimizationModel: The Pydantic model for the Strangeworks optimization model.
        """
        strangeworks_model = StrangeworksModelFactory.from_model(model)  # Make sure this is a StrangeworksModel
        model_str = strangeworks_model.to_str()  # Serialize native data from StrangeworksModel to string
        model_type = strangeworks_model.model_type.value
        model_options = json.dumps(strangeworks_model.model_options)
        strangeworks_parameters = json.dumps(strangeworks_model.strangeworks_parameters)
        return cls(
            model=model_str,  # Serialize native data from StrangeworksModel to string
            model_type=model_type,
            model_options=model_options,
            strangeworks_parameters=strangeworks_parameters,
        )


class StrangeworksOptimizationSolver(BaseModel):
    """
    A Pydantic model for Strangeworks optimization solvers.

    Attributes:
        solver (str | None): The serialized Strangeworks optimization solver.
        solver_type (str | None): The type of the Strangeworks optimization solver.
        solver_options (str | None): The options for the Strangeworks optimization solver.
        strangeworks_parameters (str | None): The parameters for the Strangeworks optimization solver.

    Methods:
        deserialize() -> StrangeworksSolver:
            Builds a StrangeworksSolver from a StrangeworksOptimizationSolver.
        from_solver(solver: StrangeworksSolver) -> StrangeworksOptimizationSolver:
            Builds a Pydantic model from a StrangeworksSolver.

    """

    solver: str | None = None
    solver_type: str | None = None
    solver_options: str | None = None
    strangeworks_parameters: str | None = None

    def deserialize(self):
        """
        Builds a StrangeworksSolver from a StrangeworksOptimizationSolver.

        Returns:
            StrangeworksSolver: The deserialized Strangeworks optimization solver.
        """
        solver = StrangeworksSolverFactory.from_solver_str(
            self.solver,
            self.solver_type,
            self.solver_options,
            self.strangeworks_parameters,
        )
        return solver

    @classmethod
    def from_solver(cls, solver):
        """
        Builds a Pydantic model from a StrangeworksSolver.

        Args:
            solver (StrangeworksSolver): The Strangeworks optimization solver.

        Returns:
            StrangeworksOptimizationSolver: The Pydantic model for the Strangeworks optimization solver.
        """
        strangeworks_solver = StrangeworksSolverFactory.from_solver(solver)
        return cls(
            solver=strangeworks_solver.to_str(),
            solver_type=strangeworks_solver.solver_type.value,
            solver_options=json.dumps(strangeworks_solver.solver_options),
            strangeworks_parameters=json.dumps(strangeworks_solver.strangeworks_parameters),
        )


class StrangeworksOptimizationSolution(BaseModel):
    """
    A Pydantic model for Strangeworks optimization solutions.

    Attributes:
        solution (str): The serialized Strangeworks optimization solution.
        solution_type (str | None): The type of the Strangeworks optimization solution.
        solution_options (str | None): The options for the Strangeworks optimization solution.
        strangeworks_parameters (str | None): The parameters for the Strangeworks optimization solution.

    Methods:
        deserialize() -> StrangeworksSolution:
            Builds a StrangeworksSolution from a StrangeworksOptimizationSolution.
        from_solution(solution: StrangeworksSolution) -> StrangeworksOptimizationSolution:
            Builds a Pydantic model from a StrangeworksSolution.

    """

    solution: str
    solution_type: str | None = None
    solution_options: str | None = None
    strangeworks_parameters: str | None = None

    def deserialize(self):
        """
        Builds a StrangeworksSolution from a StrangeworksOptimizationSolution.

        Returns:
            StrangeworksSolution: The deserialized Strangeworks optimization solution.
        """
        solution = StrangeworksSolutionFactory.from_solution_str(
            self.solution,
            self.solution_type,
            self.solution_options,
            self.strangeworks_parameters,
        )
        return solution

    @classmethod
    def from_solution(cls, solution):
        """
        Builds a Pydantic model from a StrangeworksSolution.

        Args:
            solution (StrangeworksSolution): The Strangeworks optimization solution.

        Returns:
            StrangeworksOptimizationSolution: The Pydantic model for the Strangeworks optimization solution.
        """
        strangeworks_solution = StrangeworksSolutionFactory.from_solution(solution)
        return cls(
            solution=strangeworks_solution.to_str(),
            solution_type=strangeworks_solution.solution_type.value,
            solution_options=json.dumps(strangeworks_solution.solution_options),
            strangeworks_parameters=json.dumps(strangeworks_solution.strangeworks_parameters),
        )


class StrangeworksOptimizationJob(BaseModel):
    """
    A Pydantic model for Strangeworks optimization jobs.

    Attributes:
        model (StrangeworksOptimizationModel): The Strangeworks optimization model.
        solver (StrangeworksOptimizationSolver): The Strangeworks optimization solver.
        solution (StrangeworksOptimizationSolution | None): The Strangeworks optimization solution.

    """

    model: StrangeworksOptimizationModel = Field(...)
    solver: StrangeworksOptimizationSolver = Field(...)
    solution: StrangeworksOptimizationSolution | None = Field(None)
