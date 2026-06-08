# Gradient boosting

| Field               | Type              | Orange's equivalent                | Python's default | Orange's default |
|---------------------|-------------------|------------------------------------|------------------|------------------|
| -                   | -                 | Method.                            | -                | `GBLearner`      |
| `n_estimators`      | list(int)         | Number of trees.                   | `100`            | `100`            |
| `learning_rate`     | list(float)       | Learning rate.                     | `0.1`            | `0.1`            |
| `random_state`      | list(int \| null) | Replicable training.               | `None`           | `0`              |
| `max_depth`         | list(int)         | Limit depth of individual trees.   | `3`              | `3`              |
| `min_samples_split` | list(int)         | Do not split subsets smaller than. | `2`              | `2`              |
| `subsample`         | list(float)       | Fraction of training instances.    | `1.0`            | `1`              |

> NOTE: This table describes the standard `GBLearner`. Other methods, such as `XGBLearner`, `XGBRFLearner`, and `CatGBLearner`, are selected through different learner classes and may have different default parameters.

For reference: `Orange/widgets/model/owgradientboosting.py`.
