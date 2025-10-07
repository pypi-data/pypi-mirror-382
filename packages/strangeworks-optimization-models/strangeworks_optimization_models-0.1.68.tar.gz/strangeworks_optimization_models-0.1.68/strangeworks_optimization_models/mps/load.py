import functools

import numpy as np

from .pysmps_loader import read_mps

# Deprecate this in favor of MPSFile.read_file


def load_mps(mps_file, /, *, lower={}, upper={}, lhs={}, rhs={}):
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
