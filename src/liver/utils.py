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


def root_dir(*args: Path | str) -> Path:
	"""Get root folder of the project.

	Args:
		*args: path components to join with the project root.

	Returns:
		Path: the path to the project root joined with the provided path components.
	"""
	path = Path(__file__).resolve()

	for parent in path.parents:
		if (parent / "pyproject.toml").exists():
			return parent.joinpath(*args)

	raise RuntimeError("Could not find project root!")


def config_dir(*args: Path | str) -> Path:
	"""Get configs folder.

	Args:
		*args: path components to join with the config folder.

	Returns:
		Path: the path to the configs folder joined with the provided path components.
	"""
	return root_dir("configs", *args)


def datasets_dir(*args: Path | str) -> Path:
	"""Get `datasets` folder.

	Args:
		*args: path components to join with the config folder.

	Returns:
		Path: the path to the `datasets` folder joined with the provided path components.
	"""
	return root_dir("datasets", *args)


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
