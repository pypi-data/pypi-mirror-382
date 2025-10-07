import gzip
from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
from typing import Any

import jijmodeling as jm
import networkx as nx
import numpy as np
from dimod import (
    BinaryQuadraticModel,
    ConstrainedQuadraticModel,
    DiscreteQuadraticModel,
)
from dwave.embedding import embed_ising
from minorminer import find_embedding

from strangeworks_optimization_models.problem_models import (
    AquilaNDArray,
    FujitsuModelList,
    HitachiModelList,
    MatrixMarket,
    MPSFile,
    NECProblem,
    QuboDict,
)


class StrangeworksConverter(ABC):
    model: Any

    @abstractmethod
    def convert(
        model: Any,
    ) -> (
        BinaryQuadraticModel
        | ConstrainedQuadraticModel
        | DiscreteQuadraticModel
        | jm.Problem
        | AquilaNDArray
        | QuboDict
        | NECProblem
        | MPSFile
        | FujitsuModelList
        | HitachiModelList
        | tuple
    ): ...


class StrangeworksBinaryQuadraticModelJiJProblemConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> tuple[jm.Problem, dict[str, np.ndarray], Any, Any]:
        Q = jm.Placeholder("Q", ndim=2)  # Define variable d
        Q.len_at(0, latex="N")  # Set latex expression of the length of d
        x = jm.BinaryVar("x", shape=(Q.shape[0],))  # Define binary variable
        i = jm.Element("i", belong_to=(0, Q.shape[0]))  # Define dummy index in summation
        j = jm.Element("j", belong_to=(0, Q.shape[1]))  # Define dummy index in summation
        problem = jm.Problem("simple QUBO problem")  # Create problem instance
        problem += jm.sum(i, jm.sum(j, Q[i, j] * x[i] * x[j]))  # Add objective function

        qubo = self.model.to_qubo()

        Qmat = np.zeros((self.model.num_variables, self.model.num_variables))
        map = {m: i for i, m in enumerate(self.model.variables)}
        for k, v in qubo[0].items():
            Qmat[map[k[0]], map[k[1]]] = v

        offset = self.model.offset

        feed_dict = {"Q": Qmat}
        return problem, feed_dict, map, offset


class StrangeworksMPSFileJiJProblemConverter(StrangeworksConverter):
    def __init__(self, model: MPSFile):
        self.model = model

    def convert(self) -> tuple[jm.Problem, dict[str, np.ndarray]]:
        content = self.model.data.encode("utf-8")
        with NamedTemporaryFile(mode="w+b", delete=True, suffix=".txt.gz", prefix="f") as t_file:
            gzip_file = gzip.GzipFile(mode="wb", fileobj=t_file)
            gzip_file.write(content)
            gzip_file.close()
            t_file.flush()
            t_file.seek(0)

            problem, feed_dict = jm.load_mps(t_file.name)

        return problem, feed_dict


class StrangeworksBinaryQuadraticModelQuboDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> QuboDict:
        qubo = {}
        for lin in self.model.linear:
            qubo[(str(lin), str(lin))] = self.model.linear[lin]
        for quad in self.model.quadratic:
            qubo[(str(quad[0]), str(quad[1]))] = self.model.quadratic[quad]

        # Offset term should not added to the linear terms (code below should be removed)
        if self.model.offset != 0:
            for lin in self.model.linear:
                qubo[(str(lin), str(lin))] += self.model.offset

        return QuboDict(qubo)


class StrangeworksBinaryQuadraticModelNECProblemConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> NECProblem:
        # qubo = {}
        qubo: dict[Any, Any] = {}
        for lin in self.model.linear:
            qubo[(str(lin), str(lin))] = self.model.linear[lin]
        for quad in self.model.quadratic:
            qubo[(str(quad[0]), str(quad[1]))] = self.model.quadratic[quad]

        qubo["offset"] = self.model.offset

        return NECProblem(qubo)


class StrangeworksBinaryQuadraticModelFujitsuDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> FujitsuModelList:
        bqm = self.model

        mapping = {}
        iter = 0
        for var in self.model.variables:
            mapping[var] = iter
            iter += 1
        bqm.relabel_variables(mapping)

        qubo, offset = bqm.to_qubo()
        terms = []
        for variables, coefficient in qubo.items():
            term = {"coefficient": coefficient, "polynomials": list(variables)}
            terms.append(term)

        if offset != 0:
            terms.append({"coefficient": offset, "polynomials": []})

        binary_polynomial = {"terms": terms}

        return FujitsuModelList(binary_polynomial=binary_polynomial)


class StrangeworksBinaryQuadraticModelHitachiDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel, options: dict = {}):
        self.model = model
        self.options = options

    def convert(self) -> tuple[HitachiModelList, dict[Any, Any]]:
        def get_problem_graph_from_bqm(bqm):
            problem_graph = nx.Graph()
            problem_graph.add_nodes_from(bqm.linear.keys())
            problem_graph.add_edges_from(bqm.quadratic.keys())
            return problem_graph

        def get_target_graph(solver_type):
            # Set the size of the target graph
            if solver_type == 5:
                ll = 384
            elif solver_type == 3 or solver_type == 4:
                ll = 512
            else:
                raise ValueError("machine_type must be 3, 4, or 5.")

            # Create a square graph of size l
            target_graph = nx.grid_graph(dim=[ll, ll])

            # Add the diagonal edges to the square graph.
            target_graph.add_edges_from(
                [
                    edge
                    for x in range(ll - 1)
                    for y in range(ll - 1)
                    for edge in [((x, y), (x + 1, y + 1)), ((x + 1, y), (x, y + 1))]
                ]
            )
            return target_graph

        def get_hitachi(linear: dict, quadratic: dict):
            out_list = []
            for k in quadratic.keys():
                row = []
                for t in k:
                    row.extend(list(t))
                row.append(quadratic[k])
                out_list.append(row)
            for k in linear.keys():
                if linear[k] != 0:
                    row = []
                    row.extend(list(k))
                    row.extend(list(k))  # twice on purpose
                    row.append(linear[k])
                    out_list.append(row)
            return out_list

        # bqm = self.model
        bqm = self.model.change_vartype("SPIN", inplace=False)
        linear = bqm.linear
        quadratic = bqm.quadratic

        # Get Embedding of problem onto target graph
        problem_graph = get_problem_graph_from_bqm(bqm)
        target_graph = get_target_graph(self.options.get("solver_type", 4))
        embedding = find_embedding(problem_graph, target_graph, **self.options.get("embedding_parameters", {}))

        target_linear, target_quadratic = embed_ising(linear, quadratic, embedding, target_graph)
        target_list = get_hitachi(target_linear, target_quadratic)

        return HitachiModelList(target_list), embedding


class StrangeworksBinaryQuadraticModelMatrixMarketConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> tuple[MatrixMarket, dict[Any, Any]]:
        bqm = self.model
        mapping = {}
        iter = 0
        for var in bqm.variables:
            mapping[var] = iter
            iter += 1

        qubo_str = "%%MatrixMarket matrix coordinate integer general"
        qubo_str += f"\n{len(bqm.variables)} {len(bqm.variables)} {len(bqm.linear) + len(bqm.quadratic)}"
        for k, v in bqm.linear.items():
            qubo_str += f"\n{mapping[k] + 1} {mapping[k] + 1} {v}"
        for k, v in bqm.quadratic.items():
            if mapping[k[0]] > mapping[k[1]]:
                qubo_str += f"\n{mapping[k[0]] + 1} {mapping[k[1]] + 1} {v}"
            else:
                qubo_str += f"\n{mapping[k[1]] + 1} {mapping[k[0]] + 1} {v}"

        return MatrixMarket(qubo_str), mapping


class StrangeworksConverterFactory:
    @staticmethod
    def from_model(model_from: Any, model_to: Any, options: dict = {}) -> StrangeworksConverter:
        if isinstance(model_from, BinaryQuadraticModel) and model_to == jm.Problem:
            return StrangeworksBinaryQuadraticModelJiJProblemConverter(model=model_from)
        elif isinstance(model_from, MPSFile) and model_to == jm.Problem:
            return StrangeworksMPSFileJiJProblemConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == QuboDict:
            return StrangeworksBinaryQuadraticModelQuboDictConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == NECProblem:
            return StrangeworksBinaryQuadraticModelNECProblemConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == FujitsuModelList:
            return StrangeworksBinaryQuadraticModelFujitsuDictConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == HitachiModelList:
            return StrangeworksBinaryQuadraticModelHitachiDictConverter(model=model_from, options=options)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == MatrixMarket:
            return StrangeworksBinaryQuadraticModelMatrixMarketConverter(model=model_from)
        else:
            raise ValueError("Unsupported model type")
