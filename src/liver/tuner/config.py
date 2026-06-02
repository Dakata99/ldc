from __future__ import annotations

from typing import Any

# -----------------------------------------------------------------------------
# Learner/parameter registry
# -----------------------------------------------------------------------------
# Rule:
# - The keys inside "params" are Python API parameter names.
# - "orange_opt" is only the label/name shown in Orange's GUI.
# - Python-only parameters can use orange_opt=None and exposed_in_orange=False.
#
# This lets the GUI display friendly Orange names while the runner still builds
# correct Python kwargs such as {"class_weight": "balanced"}.

LearnerSpecs = dict[str, dict[str, Any]]

LEARNER_SPECS: LearnerSpecs = {
    "LR": {
        "display_name": "Logistic Regression",
        "api_class": "LogisticRegressionLearner",
        "params": {
            "C": {
                "default": 1.0,
                "manual_values": [0.01, 0.05, 0.1, 1.0, 5.0, 10.0],
                "type": "float",
                "orange": "Regularization strength",
                "description": "Inverse regularization strength. Smaller values mean stronger regularization.",
            },
            "penalty": {
                "default": "l2",
                "manual_values": ["l2", "l1", None],
                "type": "choice",
                "orange": "Regularization type",
                "description": "Regularization penalty passed to the learner.",
            },
            "class_weight": {
                # Orange GUI idea: Balance class distribution = on/off.
                # Python API value should not be True/False for sklearn-like learners;
                # use None or "balanced" instead.
                "default": "balanced",
                "manual_values": [None, "balanced"],
                "type": "choice",
                "orange": "Balance class distribution",
                "ui_values": {
                    None: "Disabled",
                    "balanced": "Enabled / balanced",
                },
                "description": "Maps Orange's 'Balance class distribution' option to Python's class_weight parameter.",
            },
            "max_iter": {
                "default": 10000,
                "manual_values": [1000, 5000, 10000],
                "type": "int",
                "description": "Python API-only safeguard for convergence-heavy Logistic Regression runs.",
            },
            "random_state": {
                "default": 0,
                "manual_values": [None, 0, 42],
                "type": "int",
                "description": "Python API-only safeguard for randomness.",
            },
        },
    },
    "DT": {
        "display_name": "Tree",
        "api_class": "TreeLearner",
        "params": {
            "binarize": {
                "default": True,
                "manual_values": [False, True],
                "type": "bool",
                "orange": "Induce binary tree",
                "description": "",
            },
            "min_samples_leaf": {
                "default": 2,
                "manual_values": [1, 3, 5],
                "type": "int",
                "orange": "Min. number of instances in leaves",
                "description": "Minimum samples in a leaf. Helps reduce overfitting.",
            },
            "min_samples_split": {
                "default": 5,
                "manual_values": [2, 5, 10],
                "type": "int",
                "orange": "Do not split subsets smaller than",
                "description": "Minimum number of samples required to split an internal node.",
            },
            "max_depth": {
                "default": 100,
                "manual_values": [None, 5, 10, 20],
                "type": "optional[int]",
                "orange": "Limit maximal tree depth",
                "description": "None means no explicit maximum depth.",
            },
            "sufficient_majority": {
                "default": 0.95,
                "manual_values": [None, 0.9, 0.95, 0.99],
                "type": "optional[float]",
                "orange": "Stop when majority reaches",
                "description": "",
            }
        },
    },
    "RF": {
        "display_name": "Random Forest",
        "api_class": "RandomForestLearner",
        "params": {
            "n_estimators": {
                "default": 10,
                "manual_values": [50, 100, 200],
                "type": "int",
                "orange": "Number of trees",
                "description": "Number of trees in the forest.",
            },
            "max_features": {
                "default": "sqrt",
                "manual_values": ["sqrt", "log2", None],
                "type": "choice",
                "orange": "Number of attributes considered at each split",
                "description": "None usually means all features; sqrt/log2 restrict the split search.",
            },
            "random_state": {
                "default": 0,
                "manual_values": [None, 0, 42],
                "type": "optional[int]",
                "orange": "Replicable training",
                "description": "",
            },
            "class_weight": {
                "default": "balanced",
                "manual_values": [None, "balanced"],
                "type": "choice",
                "orange": "Balance class distribution",
                "ui_values": {
                    None: "Disabled",
                    "balanced": "Enabled / balanced",
                },
                "description": "Maps Orange's class balancing option to Python's class_weight parameter.",
            },
            "max_depth": {
                "default": None,
                "manual_values": [None, 10, 20],
                "type": "optional[int]",
                "orange": "Limit depth of individual trees",
                "description": "None means unconstrained depth.",
            },
            "min_samples_split": {
                "default": 5,
                "manual_values": [2, 5, 10],
                "type": "int",
                "orange": "Do not split subsets smaller than",
                "description": "Minimum samples required to split an internal tree node.",
            }
        },
    },
    "GB": {
        "display_name": "Gradient Boosting",
        "api_class": "GBClassifier",
        "params": {
            # TODO: add method - XGBoost, CatGB, etc.
            "n_estimators": {
                "default": 100,
                "manual_values": [50, 100, 200],
                "type": "int",
                "orange": "Number of trees",
                "description": "Number of boosting stages.",
            },
            "learning_rate": {
                "default": 0.1,
                "manual_values": [0.03, 0.05, 0.1],
                "type": "float",
                "orange": "Learning rate",
                "description": "Shrinkage applied to each tree contribution.",
            },
            "random_state": {
                "default": 0,
                "manual_values": [None, 0, 42],
                "type": "optional[int]",
                "orange": "Replicable training",
                "description": "",
            },
            "max_depth": {
                "default": 3,
                "manual_values": [2, 3, 5],
                "type": "int",
                "orange": "Limit depth of individual trees",
                "description": "Depth of weak learners used by boosting.",
            },
            "min_samples_split": {
                "default": 2,
                "manual_values": [2, 5, 10],
                "type": "int",
                "orange": "Do not split subsets smaller than",
                "description": "Minimum samples required to split an internal tree node.",
            },
            "subsample": {
                "default": 1.0,
                "manual_values": [0.5, 0.75, 1.0],
                "type": "float",
                "orange": "Fraction of training instances",
                "description": "Fraction of samples used for fitting individual base learners.",
            }
        },
    },
    "NN": {
        "display_name": "Neural Network",
        "api_class": "NNClassificationLearner",
        "params": {
            "hidden_layer_sizes": {
                "default": [100],
                "manual_values": [[100], [50, 50], [100, 50]],
                "type": "list[int]",
                "orange": "Neurons in hidden layers",
                "description": "List-like architecture. Manual mode must use a list of lists.",
            },
            "activation": {
                "default": "relu",
                "manual_values": ["relu", "tanh"],
                "type": "choice",
                "orange": "Activation",
                "description": "Activation function for hidden layers.",
            },
            "solver": {
                "default": "adam",
                "manual_values": ["lbfgs", "adam"],
                "type": "choice",
                "orange": "Solver",
                "description": "Algorithm to use in the optimization.",
            },
            "alpha": {
                "default": 0.0001,
                "manual_values": [0.0001, 0.001, 0.01],
                "type": "float",
                "orange": "Regularization, α",
                "description": "L2 regularization term for the neural network.",
            },
            "max_iter": {
                "default": 200,
                "manual_values": [200, 500, 1000],
                "type": "int",
                "orange": "Maximal number of iterations",
                "description": "",
            },
            "random_state": {
                "default": 1,
                "manual_values": [None, 1, 42],
                "type": "optional[int]",
                "orange": "Replicable training",
                "description": "",
            },
        },
    },
    "SVM": {
        "display_name": "SVM",
        "api_class": "SVMLearner",
        "params": {
            "C": {
                "default": 1.0,
                "manual_values": [0.1, 1.0, 5.0, 10.0],
                "type": "float",
                "orange": "Cost",
                "description": "Penalty/cost parameter.",
            },
            "kernel": {
                "default": "rbf",
                "manual_values": ["rbf", "linear", "poly", "sigmoid"],
                "type": "choice",
                "orange": "Kernel",
                "description": "Kernel function.",
            },
            "gamma": {
                "default": "auto",
                "manual_values": ["auto", 0.01, 0.1, 1.0],
                "type": "choice|float",
                "orange": "g",
                "description": "Kernel coefficient. Keep values conservative; SVM grids can explode quickly.",
            },
            "coef0": {
                "default": 1.0,
                "manual_values": [0.0, 1.0, 10.0],
                "type": "float",
                "orange": "c",
                "description": "TODO",
            },
            "tol": {
                "default": 0.001,
                "manual_values": [0.0001, 0.001, 0.01],
                "type": "float",
                "orange": "Numerical tolerance",
                "description": "",
            },
            "max_iter": {
                "default": 100,
                "manual_values": [-1, 500, 1000, 5000],
                "type": "list[int]",
                "orange": "Iteration limit",
                "description": "-1 means unlimited in the Python API.",
            },
            "degree": {
                "default": 3,
                "manual_values": [2, 3, 5],
                "type": "int",
                "orange": "d",
                "description": "Only relevant for polynomial kernel.",
            },
            "probability": {
                "default": True,
                "manual_values": [False, True],
                "type": "bool",
                "description": "Orange GUI passes this internally.",
            }
        },
    },
}

LEARNER_PAIRS = [
    ("LR", "DT"),
    ("RF", "GB"),
    ("NN", "SVM"),
]
