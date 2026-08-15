from functools import partial
from itertools import chain
from pathlib import Path
from typing import Any

from loguru import logger
import mlflow
from Orange.data import Table
from Orange.evaluation import AUC, CA, F1, MatthewsCorrCoefficient, Precision, Recall
from Orange.evaluation.testing import CrossValidation, TestOnTestData
from Orange.preprocess import Average, Continuize, Impute, Normalize, PreprocessorList
import pandas as pd

from .load import load_configuration, load_dataset
from .utils import create_learners, profiler, root_dir

CSV_FILENAME: str = "{config}-{method}.csv"


EXPERIMENTS: dict[int, str] = {
	1: "Multiclass classification for Indian dataset",
	2: "Binary classification for Indian dataset",
	3: "Binary classification for all 3 datasets",
}

CROSS_VALIDATION: str = "cross-validation"
HOLD_OUT: str = "hold-out"


class TestAndScore:
	def __init__(self, learners: list[Any]):
		self._learners = learners
		self._preprocessor = PreprocessorList(
			preprocessors=(
				# Average/Most frequent
				Impute(method=Average()),
				# One-hot encoding/One feature per value
				Continuize(multinomial_treatment=Continuize.Indicators),
				# Standardization (z-score normalization)
				Normalize(norm_type=Normalize.NormalizeBySD),
			)
		)
		self._scores = None

	@profiler  # type: ignore[untyped-decorator]
	def train(self, train: Table, test: Table, method: str) -> None:
		"""Method for training learnears.

		Args:
			train (Table): Train data.
			test (Table): Test data.
			method (str): Evaluation method.
		"""

		# Evaluate models with the chosen method
		if method == CROSS_VALIDATION:
			logger.info(
				f"{CROSS_VALIDATION.capitalize()}: evaluating {len(self._learners)} learners..."
			)

			def progress_callback(progress: float) -> None:
				logger.info("Progress: {}%", round(progress * 100, 1))

			evaluator = CrossValidation()
			self._scores = evaluator(
				train,
				self._learners,
				preprocessor=self._preprocessor,
				callback=progress_callback,
			)
		else:
			logger.info(f"{HOLD_OUT.capitalize()}: evaluating {len(self._learners)} learners...")

			# Evaluate using TestOnTestData (train on train set, test on test set)
			def progress_callback(progress: float) -> None:
				done = round(progress * len(self._learners))
				logger.info(
					"Finished {}/{} learners ({:.2f}%)",
					done,
					len(self._learners),
					progress * 100,
				)

			# Set store_data to True if we want to keep the augmented data with predictions, probabilities, etc.
			evaluator = TestOnTestData(store_data=False)
			self._scores = evaluator(
				train,
				test,
				self._learners,
				preprocessor=self._preprocessor,
				callback=progress_callback,
			)

	def eval(self, exprid: int, output_filename: str) -> None:
		"""Metrics evalution."""
		sick_index = None
		# healthy_index = None
		if exprid in [2, 3] and self._scores is not None:
			sick_index = list(self._scores.domain.class_var.values).index("Sick")
			# healthy_index = list(self._scores.domain.class_var.values).index("Healthy")

		# NOTE: priority of the metrics is preserved from here!
		# Will be ordered in the CSV file as here and plotting will keep this priority!
		metrics: dict[int, dict[str, Any]] = {
			1: {
				"recall_weighted": partial(Recall, target=None, average="weighted"),
				"f1_weighted": partial(F1, target=None, average="weighted"),
				"mcc": MatthewsCorrCoefficient,
				"precision_weighted": partial(Precision, target=None, average="weighted"),
				"auc": AUC,
				"ca": CA,
			},
			2: {
				"recall_sick": partial(Recall, target=sick_index),
				"recall_weighted": partial(Recall, average="weighted"),
				"f1_sick": partial(F1, target=sick_index),
				"f1_weighted": partial(F1, average="weighted"),
				"mcc": MatthewsCorrCoefficient,
				"precision_sick": partial(Precision, target=sick_index),
				"auc": AUC,
				"ca": CA,
			},
			3: {
				"recall_sick": partial(Recall, target=sick_index),
				"recall_weighted": partial(Recall, average="weighted"),
				"f1_sick": partial(F1, target=sick_index),
				"f1_weighted": partial(F1, average="weighted"),
				"mcc": MatthewsCorrCoefficient,
				"precision_sick": partial(Precision, target=sick_index),
				"auc": AUC,
				"ca": CA,
			},
		}

		# Write results into a CSV file
		rows = []
		# Loop through learners
		with mlflow.start_run(run_name=output_filename.removesuffix(".csv")):
			for i, learner in enumerate(self._learners):
				row = {"Learner": repr(learner)}

				with mlflow.start_run(run_name=repr(learner), nested=True):
					mlflow.set_tag("learner_type", type(learner).__name__)
					mlflow.log_param("learner", repr(learner))

					for name, metric in metrics[exprid].items():
						values = metric(self._scores)
						row[name] = values[i]
						mlflow.log_metric(key=name, value=float(values[i]))
						rows.append(row)

		df = pd.DataFrame(rows)
		logger.success(df.to_string(index=False))

		results_dir: Path = root_dir("results", f"experiment{exprid}")
		if not results_dir.exists():
			results_dir.mkdir(parents=True)
		df.to_csv(results_dir / output_filename, index=False)
		mlflow.log_artifact(results_dir / output_filename)
		mlflow.log_table(df, f'experiment{exprid}-{output_filename.removesuffix(".csv")}.json')


def main(
	exprid: int, method: str, learners_group: list[str], configuration: str = "default"
) -> None:
	"""Main function for evaluation an experiment."""
	logger.info(f"Running experiment: {EXPERIMENTS[exprid]}")

	# 1) Load train, test data
	train, test = load_dataset(exprid)

	# 2) Load configuration and create learners
	config = load_configuration(configuration)
	learners = create_learners(config)
	logger.debug(learners)

	# 3) Evaluate
	learners_to_evaluate = []
	if learners_group is None:
		learners_to_evaluate = list(chain.from_iterable(learners.values()))
	else:
		for group in learners_group:
			if group in learners:
				learners_to_evaluate.extend(learners[group])

	# MLFlow experiment settings
	mlflow.set_experiment(f'expriment{exprid}')
	mlflow.set_experiment_tags({
		'experiment': exprid,
		'config': configuration,
		'method': method
	})

	ts = TestAndScore(learners_to_evaluate)
	ts.train(train, test, method)
	ts.eval(exprid, CSV_FILENAME.format(config=configuration, method=method))
