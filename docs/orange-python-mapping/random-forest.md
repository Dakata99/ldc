# Random forest

| Field               | Type                     | Orange's equivalent                            | Python's default | Orange's default               |
|---------------------|--------------------------|------------------------------------------------|------------------|--------------------------------|
| `n_estimators`      | list(int)                | Number of trees.                               | `10`             | `10`                           |
| `max_features`      | list(int \| str \| null) | Number of attributes considered at each split. | `sqrt`           | Disabled: `sqrt`, enabled: `5` |
| `random_state`      | list(int \| null)        | Replicable training.                           | `None`           | Disabled: `None`, enabled: `0` |
| `class_weight`      | list(str \| null)        | Balance class distribution.                    | `None`           | `None`                         |
| `max_depth`         | list(int \| null)        | Limit depth of individual trees.               | `None`           | Disabled: `None`, enabled: `3` |
| `min_samples_split` | list(int)                | Do not split subsets smaller than.             | `2`              | `5`                            |

For reference: `Orange/widgets/model/owrandomforest.py`.