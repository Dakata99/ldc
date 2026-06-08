# Neural network

| Field                | Type              | Orange's equivalent           | Python's default | Orange's default |
|----------------------|-------------------|-------------------------------|------------------|------------------|
| `hidden_layer_sizes` | list(list(int))   | Neurons in hidden layers.     | `(100,)`         | `(100,)`         |
| `activation`         | list(str)         | Activation.                   | `relu`           | `relu`           |
| `solver`             | list(str)         | Solver.                       | `adam`           | `adam`           |
| `alpha`              | list(float)       | Regularization, alpha.        | `0.0001`         | `0.0001`         |
| `max_iter`           | list(int)         | Maximal number of iterations. | `200`            | `200`            |
| `random_state`       | list(int \| null) | Replicable training.          | `None`           | `1`              |

For reference: `Orange/widgets/model/owneuralnetwork.py`.
