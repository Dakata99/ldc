# Experimental machine learning study for liver disease classification

This project aims to evaluate a portfolio of machine learning algorithms for liver diseases classification.
The experimental study consists of 3 experimental scenarios:

1) Multiclass classification of the largest dataset
2) Binary classification of the largest dataset
3) Binary classification of all 3 datasets

## Prerequisites

Install `uv` tool:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Datasets

The following datasets are being used:
- [indian-liver-disease-dataset](https://www.kaggle.com/datasets/paramjeetsinghds/indian-liver-disease-dataset)
- [hcv-data](https://www.kaggle.com/datasets/visheshkkl/hcv-data)
- [liver-data](https://www.kaggle.com/datasets/aichamalouche/liver-data)

## How to run?

To evaluate the experiments, first set up the environment:
```bash
source setupenv
```

Then the `liver` command will be present and you can run `liver -h` to see what it does:
```bash
$ liver -h
usage: liver [-h] --experiment {1,2,3} [--debug]
             [--learners-group {logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} [{logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} ...]]
             [--config {default,global,experiment1,experiment2,experiment3}] [--plot-only]

options:
  -h, --help            show this help message and exit
  --experiment {1,2,3}
  --debug               Enable debug logging
  --learners-group {logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} [{logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} ...]
                        Run specific family(ies) of learners.
  --config {default,global,experiment1,experiment2,experiment3}
                        Configuration to use for the experiment
  --plot-only           Plot only on already existing results.
```

To check the generated results/report, run:
```bash
wslview results/experiment<experiment>-<config>.csv
wslview reports/experiment<experiment>-<config>.html
```

## Configuration files

Configuration files are located in the `configs` folder.
The structure is as follows:
```json
{
    "logistic-regression": {
        "penalty": [
            "l2"
        ],
        "C": [
            1.0
        ],
        "class_weight": [
            null
        ]
    },
    "random-forest": {...},
    "svm": {...},
    "gradient-boosting": {...},
    "tree": {...},
    "neural-network": {...}
}
```
where the parameters for each learner are added.

## Known issues and limitations

- Disabled GUI options should usually be represented by omitting the parameter from the JSON, not by passing `null`. Passing `null` becomes `None` in Python and is only valid for parameters whose API explicitly accepts `None`, such as `class_weight`, `max_depth`, or `random_state`.
- `Orange.evaluation.testing.sample()` uses a different splitting implementation/row-selection logic than Orange GUI’s Data Sampler widget, so the same `n=0.8`, `stratified=True`, and `random_state=42` do not guarantee the same train/test rows.

## TODO

- Make `default` JSON files for Orange and for Python, i.e. `default-ow` and `default-py`.
- Make full default JSON with all parameters described for each learner.
