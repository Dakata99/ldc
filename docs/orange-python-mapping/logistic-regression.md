# Logistic regression

| Field               | Type            | Orange's equivalent         | Python's default | Orange's default |
|---------------------|-----------------|-----------------------------|------------------|------------------|
| `penalty`           | list(str\|null) | Regularization type.        | `l2`             | `l2`             |
| `C`                 | list(float)     | Strength (weak to strong).  | `1.0`            | `1.0`            |
| `class_weight`      | list(str\|null) | Balance class distribution. | `None`           | `None`           |

Additional arguments, not exposed by Orange GUI:

| Field               | Python's default | Orange's default |
|---------------------|------------------|------------------|
| `dual`              | `False`          | `False`          |
| `tol`               | `0.0001`         | `0.0001`         |
| `random_state`      | `None`           | `0`              |
| `max_iter`          | `100`            | `10000`          |
| `fit_intercept`     | `True`           | `True`           |
| `intercept_scaling` | `1`              | `1.0`            |

> NOTE: `class_weight` parameter accepts `None` or `balanced` values.

For reference: `Orange/widgets/model/owlogisticregression.py`.
