import functools
import tempfile

import numpy as np
import pyqubo  # type: ignore
from dimod import BinaryQuadraticModel
from pyqubo import cpp_pyqubo  # type: ignore

from .pysmps_loader import read_mps


def mps_to_dict(problem, /, *, lower={}, upper={}, lhs={}, rhs={}):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mps") as f:
        f.write(problem)
        f.flush()
        mps_file = f.name

        mps = read_mps(mps_file)

    problem = {}

    problem["binary_keys"] = sorted(
        k for (k, v) in mps.get_variables().items() if v["type"] == "Integer" and v["lower"] == 0 and v["upper"] == 1
    )
    problem["continuous_keys"] = sorted(k for (k, v) in mps.get_variables().items() if (v["type"] == "Continuous"))
    problem["constraint_keys"] = sorted(mps.constraint_names())
    # problem["constraint_keys"] = sorted(mps.constraints.keys())

    problem["continuous_lower"] = {
        k: max(mps.get_variables()[k]["lower"], lower[k] if k in lower else -np.inf) for k in problem["continuous_keys"]
    }
    problem["continuous_upper"] = {
        k: min(mps.get_variables()[k]["upper"], upper[k] if k in upper else +np.inf) for k in problem["continuous_keys"]
    }

    problem["obj_offset"] = -mps.get_offsets()[mps.objective_names()[0]]
    # if "B" in mps.offsets and "obj" in mps.offsets["B"]:
    #     problem["obj_offset"] = - mps.offsets["B"]["OBJ"]
    # else:
    #     problem["obj_offset"] = 0.0

    problem["obj_1st"] = dict(mps.get_objectives()[mps.objective_names()[0]]["coefficients"].items())
    # problem["obj_1st"] = dict(mps.objectives["OBJ"]["coefficients"].items())

    problem["constraint_1st"] = {
        c: dict(mps.get_constraints()[c]["coefficients"].items()) for c in problem["constraint_keys"]
    }
    problem["constraint_lower"] = {
        c: max(_load_lhs_rhs(mps, c)[0], lhs[c] if c in lhs else -np.inf) for c in problem["constraint_keys"]
    }
    problem["constraint_upper"] = {
        c: min(_load_lhs_rhs(mps, c)[1], rhs[c] if c in rhs else +np.inf) for c in problem["constraint_keys"]
    }

    return problem


@functools.cache
def _load_lhs_rhs(mps, c):
    d = mps.get_constraints()[c]

    if d["type"] == "E":
        lhs = -np.inf
        rhs = +np.inf
        if c in mps.get_rhs():
            lhs = mps.get_rhs()[c]
            rhs = mps.get_rhs()[c]
        if mps.get_curr_range() != -1 and c in mps.get_ranges():
            lhs += mps.get_ranges()[c]["lower"]
            rhs += mps.get_ranges()[c]["upper"]
    elif d["type"] == "L":
        lhs = -np.inf
        rhs = +np.inf
        if c in mps.get_rhs():
            rhs = mps.get_rhs()[c]
        if mps.get_curr_range() != -1 and c in mps.get_ranges():
            lhs = mps.get_rhs()[c] + mps.get_ranges()[c]["lower"]
            rhs = mps.get_rhs()[c] + mps.get_ranges()[c]["upper"]
    elif d["type"] == "G":
        lhs = -np.inf
        rhs = +np.inf
        if c in mps.get_rhs():
            lhs = mps.get_rhs()[c]
        if mps.get_curr_range() != -1 and c in mps.get_ranges():
            lhs = mps.get_rhs()[c] + mps.get_ranges()[c]["lower"]
            rhs = mps.get_rhs()[c] + mps.get_ranges()[c]["upper"]

    lval = round(
        sum(
            min(v * mps.get_variables()[k]["lower"], v * mps.get_variables()[k]["upper"])
            for (k, v) in d["coefficients"].items()
        ),
        4,
    )
    rval = round(
        sum(
            max(v * mps.get_variables()[k]["lower"], v * mps.get_variables()[k]["upper"])
            for (k, v) in d["coefficients"].items()
        ),
        4,
    )

    return max(lhs, lval), min(rhs, rval)


def mps_to_bqm(problem, alpha) -> tuple[BinaryQuadraticModel, cpp_pyqubo.Model]:
    problem_dict = mps_to_dict(problem)

    (pyquboBinary, pyquboContinuous, pyquboSlack) = _prepare_variables(problem_dict)

    hamiltonian = _prepare_hamiltonian(problem_dict, pyquboBinary, pyquboContinuous, pyquboSlack)

    matrix, offset = _prepare_qubo_matrix(hamiltonian, alpha)

    return BinaryQuadraticModel.from_qubo(matrix, offset), hamiltonian


def _prepare_variables(problem):
    pyquboBinary = {k: pyqubo.Binary(k) for k in problem["binary_keys"]}

    pyquboContinuous = {
        k: (
            pyqubo.Binary(k) * (problem["continuous_upper"][k] - problem["continuous_lower"][k])
            + problem["continuous_lower"][k]
        )
        for k in problem["continuous_keys"]
    }

    pyquboSlack = {
        c: (
            pyqubo.Binary(c) * (problem["constraint_upper"][c] - problem["constraint_lower"][c])
            + problem["constraint_lower"][c]
        )
        for c in problem["constraint_keys"]
    }

    return (pyquboBinary, pyquboContinuous, pyquboSlack)


def _prepare_hamiltonian(problem, pyquboBinary, pyquboContinuous, pyquboSlack) -> cpp_pyqubo.Model:
    pyquboAll = pyquboBinary | pyquboContinuous

    hamiltonian = (
        problem["obj_offset"]
        + sum(v * pyquboAll[k] for (k, v) in problem["obj_1st"].items())
        + pyqubo.Placeholder("Alpha")
        * sum(
            (sum(v * pyquboAll[k] for (k, v) in d.items()) - pyquboSlack[c]) ** 2
            / max(problem["constraint_upper"][c] - problem["constraint_lower"][c], max(abs(v) for v in d.values())) ** 2
            for (c, d) in problem["constraint_1st"].items()
        )
    )
    compiled_hamiltonian = hamiltonian.compile()
    return compiled_hamiltonian


def _prepare_qubo_matrix(model, alpha):
    qubo, offset = model.to_qubo(feed_dict={"Alpha": alpha})

    k2i = {k: i for (i, k) in enumerate(model.variables)}

    return {(max(k2i[k1], k2i[k2]), min(k2i[k1], k2i[k2])): v for ((k1, k2), v) in qubo.items()}, offset
