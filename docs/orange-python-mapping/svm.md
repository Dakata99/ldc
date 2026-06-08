# Support vector machine (SVM)

| Field         | Type               | Orange's equivalent  | Python's default | Orange's default | Notes                                   |
|---------------|--------------------|--------------------- |------------------|------------------|-----------------------------------------|
| `C`           | list(float)        | Cost.                | `1.0`            | `1.0`            | Used by C-SVM.                          |
| `kernel`      | list(str)          | Kernel.              | `rbf`            | `rbf`            | `linear`, `poly`, `rbf`, `sigmoid`.     |
| `gamma`       | list(float \| str) | g                    | `auto`           | `auto`           | Used by Polynomial, RBF and Sigmoid.    |
| `coef0`       | list(float)        | c                    | `0.0`            | `1.0`            | Used by Polynomial and Sigmoid kernels. |
| `tol`         | list(float)        | Numerical tolerance. | `0.001`          | `0.001`          |                                         |
| `max_iter`    | list(int)          | Iteration limit.     | `-1`             | `100`            | `-1` means unlimited in the Python API. |
| `degree`      | list(int)          | d                    | `3`              | `3`              | Relevant for polynomial kernel.         |
| `probability` | list(bool)         |                      | `False`          | `True`           | Orange GUI passes this internally.      |

> NOTE: The configuration for this learner uses lists of dicts since different kernels have different parameters.

For reference: `Orange/widgets/model/owsvm.py`.
