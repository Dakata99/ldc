import argparse
from pathlib import Path

import argcomplete

AVAILABLE_CONFIGS: tuple[str, ...] = (
	"default",
	"default-full",
	"global",
	"experiment1",
	"experiment2",
	"experiment3",
	"experiment3-default",  # Tied for experiment 3
)

CROSS_VALIDATION: str = "cross-validation"
HOLD_OUT: str = "hold-out"


def setup_logging(debug: bool = False) -> None:
	import sys

	from loguru import logger

	logger.remove()
	logger.add(
		sys.stderr,
		level="DEBUG" if debug else "INFO",
	)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--experiment", type=int, choices=[1, 2, 3])
	parser.add_argument("--debug", action="store_true", help="Enable debug logging")
	parser.add_argument(
		"--learners-group",
		choices=[
			"logistic-regression",
			"random-forest",
			"tree",
			"gradient-boosting",
			"neural-network",
			"svm",
		],
		nargs="+",
		default=None,
		help="Run specific family(ies) of learners.",
	)
	parser.add_argument(
		"--config",
		type=str,
		choices=AVAILABLE_CONFIGS,
		default="default",
		help="Configuration to use for the experiment",
	)
	parser.add_argument(
		"--plot-only",
		nargs="?",
		type=Path,
		default=None,
		metavar="RESULTS_DIR",
		help="Plot only on already existing results.",
	)
	mt = parser.add_mutually_exclusive_group()
	mt.add_argument(
		"--cross-validation",
		action="store_true",
		default=False,
		help="Use Cross Validation method.",
	)
	mt.add_argument(
		"--hold-out",
		action="store_true",
		default=True,
		help="Use Hold-out (TestOnTestData) method.",
	)
	argcomplete.autocomplete(parser)
	args = parser.parse_args()

	# Set up logging
	setup_logging(args.debug)

	# Method for evaluation, hold-out = test on test data
	method = CROSS_VALIDATION if args.cross_validation else HOLD_OUT

	if args.experiment and not args.plot_only:
		# Run the analysis for the specified experiment
		from .core import run_analysis

		run_analysis(args.experiment, method, args.learners_group, args.config)
	elif args.plot_only:
		# Plot the results for the specified experiment
		from .plot import main as plot

		path: Path = args.plot_only
		if not path.is_file():
			raise FileNotFoundError(f"No such file: {path}")
		elif not path.suffix == ".csv":
			raise FileNotFoundError("Invalid file extension!")

		experiment = path.parent.stem.replace("experiment", "")
		csv: list[str] = path.stem.split("-")
		config: str = csv[0]
		mtd: str = "-".join(csv[1:])

		plot(experiment, mtd, config)
