# make_spirals
`make_spirals` generates a synthetic data set composed of interlaced Archimedean spirals.

```python
import matplotlib.pyplot as plt
X, y = make_spirals(random_state=0)
plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.bwr, alpha=0.5)
```

![example](docs/images/example.png)

Install `make_spirals` using `pip`:

```
pip install make_spirals
```

`make_spirals` allows its customization. With `n_samples` (default `500`) you control total number of points equally divided among classes and with `noise` (default `1`) standard deviation of Gaussian noise can be added to the data.

```python
import matplotlib.pyplot as plt
X, y = make_spirals(n_samples=1000, noise=2, random_state=0)
plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.bwr, alpha=0.5)
```

![example](docs/images/example-with-n_samples-and-noise.png)

Using `margin` (default `.5`) you define then separation between each spiral.

```python
import matplotlib.pyplot as plt
X, y = make_spirals(n_samples=1000, noise=2, margin=1.5, random_state=0)
plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.bwr, alpha=0.5)
```

![example](docs/images/example-with-margin.png)

By setting `n_loops` (default `2`) you fix the number of loops of each spiral.

```python
import matplotlib.pyplot as plt
X, y = make_spirals(n_samples=1000, n_loops=4, random_state=0)
plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.bwr, alpha=0.5)
```

![example](docs/images/example-with-n_loops.png)

Finally, `n_classes` (default `2`) determines the total number of classes (i.e., spirals) to include in the dataset.
 
 ```python
import matplotlib.pyplot as plt
X, y = make_spirals(n_samples=1000, n_classes=4, margin=1, n_loops=1, random_state=0)
plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.viridis, alpha=0.5)
```

![example](docs/images/example-with-n_classes.png)