![Tests](https://github.com/strangeworks/strangeworks-optimization-models/actions/workflows/cron_test.yml/badge.svg)

# Strangeworks-Optimization-Models
Pydantic models for use with Strangeworks Optimization API
- StrangeworksModel is an abstract base class for all Strangeworks optimization models.

These are all in the `strangeworks_optimization_models` module.

## Problem Models
In `problem_models` we have data structures representing the problems to be solved. these take the form

- Model is the native model used outside strangeowrks
- Model type is an enum of the types of native models
- StrangeworksModelType is an enum that defines the types of models available. These include:
    - BinaryQuadraticModel
    - ConstrainedQuadraticModel
    - DiscreteQuadraticModel
    - JiJProblem
    - AquilaModel
    - QuboDict
    - MPSFile
    - HitachiModel
- Each model has its own class, such as MPSFile, QuboDict, AquilaNDArray, and HitachiModelList. These classes contain the data for each model.


## Solver Models

Ways to specify solvers. Right now they are all basically `provider.solver`

## Solution Models
In `solution_models` we have data structures representing the solutions to the problems. These take the form:

- Solution is the native solution used outside strangeworks
- Solution type is an enum of the types of native solutions

The solution models also include methods for converting the solution to a string and from a string, similar to the problem models.
