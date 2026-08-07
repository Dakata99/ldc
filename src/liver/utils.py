from __future__ import annotations

from collections.abc import Callable
import functools
from itertools import product
from pathlib import Path
import time
from typing import Any, ParamSpec, TypeVar

from loguru import logger
from Orange.classification import (
	GBClassifier,
	LogisticRegressionLearner,
	NNClassificationLearner,
	RandomForestLearner,
	SVMLearner,
	TreeLearner,
)

LEARNERS_MAPPING: dict[str | Any, Any] = {
	"logistic-regression": LogisticRegressionLearner,
	"random-forest": RandomForestLearner,
	"tree": TreeLearner,
	"gradient-boosting": GBClassifier,
	"neural-network": NNClassificationLearner,
	"svm": SVMLearner,
}

P = ParamSpec("P")
R = TypeVar("R")


def root(*args: Path | str) -> Path:
	"""Get root folder of the project.
	TODO: maybe find a better way?

	Args:
		*args: path components to join with the project root.

	Returns:
		Path: the path to the project root joined with the provided path components.
	"""
	return Path(__file__).resolve().parents[2].joinpath(*args)


def create_learners(config: dict[str, Any]) -> dict[str, list[Any]]:
	"""Create all combinations of learners by the specified configuration."""

	# Helper function to get all combinations of hyperparameters
	def get_combinations(params: dict[Any, Any]) -> list[dict[Any, Any]]:
		return [dict(zip(params.keys(), combo, strict=True)) for combo in product(*params.values())]

	learners: dict[str, list[Any]] = {}
	for key, value in config.items():
		combos = []
		if isinstance(value, list):  # SVM-specific
			for subconfig in value:
				combos.extend(get_combinations(subconfig))
		else:
			combos = get_combinations(value)
		logger.debug(f"Combinations for {key} ({len(combos)}): {combos}")
		learners[key] = [LEARNERS_MAPPING[key](**combo) for combo in combos]
		logger.debug(learners[key])

	logger.debug(learners)

	return learners


def profiler(func: Callable[P, R]) -> Callable[P, R]:
	@functools.wraps(func)
	def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
		start_time = time.perf_counter()
		result = func(*args, **kwargs)
		end_time = time.perf_counter() - start_time
		logger.info(
			f"Function '{func.__name__}' executed in {end_time / 60:.2f} mins ({end_time:.4f} seconds)"
		)
		return result

	return wrapper
