# Tree

| Field                 | Type              | Orange's equivalent                 | Python's default | Orange's default |
|-----------------------|-------------------|-------------------------------------|------------------|------------------|
| `binarize`            | list(bool)        | Induce binary tree.                 | `False`          | `True`           |
| `min_samples_leaf`    | list(int)         | Min. number of instances in leaves. | `1`              | `2`              |
| `min_samples_split`   | list(int)         | Do not split subsets smaller than.  | `2`              | `5`              |
| `max_depth`           | list(int \| null) | Limit maximal tree depth.           | `None`           | `100`            |
| `sufficient_majority` | list(float)       | Stop when majority reaches.         | `0.95`           | `0.95`           |

For reference: `Orange/widgets/model/owtree.py`.
