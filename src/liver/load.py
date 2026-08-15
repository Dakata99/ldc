import json
from pathlib import Path
from typing import Any

from loguru import logger
from Orange.data import Table

from .cli import AVAILABLE_CONFIGS
from .utils import config_dir, datasets_dir


def load_dataset(datasetid: int) -> tuple[Table, Table]:
	"""Load file for the specified dataset.

	Args:
		datasetid (int):    Id of the dataset to load.
							Available options are: '1', '2', '3'.
	"""
	experiment: str = f"experiment{datasetid}"

	path: Path = datasets_dir(experiment)
	train: Path = path / "train-data.tab"
	test: Path = path / "test-data.tab"

	if path is None:
		raise RuntimeError(f"No such dataset: {experiment}")
	elif not path.exists():
		raise FileNotFoundError(f"Dataset file does not exist: {path}")
	elif not train.exists() or not test.exists():
		raise FileNotFoundError("Either train or test, or both files don't exist!")

	train_data: Table = Table(str(train))
	test_data: Table = Table(str(test))

	logger.success(f"Train data loaded successfully: {train}")
	logger.debug("Loaded rows: {}", len(train_data))

	logger.success(f"Test data loaded successfully: {test}")
	logger.debug("Loaded rows: {}", len(test_data))

	return train_data, test_data


def load_configuration(config: str = "default") -> Any:
	"""Load configuration (JSON) file."""

	if config not in AVAILABLE_CONFIGS:
		raise ValueError(
			f"Please, specify a valid configuration! Available are: {AVAILABLE_CONFIGS}"
		)

	configuration = config_dir(f"{config}.json")

	with open(configuration) as fd:
		data = json.load(fd)

	logger.success(f"Configuration loaded: {configuration}")

	return data
