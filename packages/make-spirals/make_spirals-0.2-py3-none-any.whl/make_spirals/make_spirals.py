import numpy as np
from sklearn import utils
import math
 
def make_spirals(n_samples=500, n_classes=2, shuffle=True, noise=1, n_loops=2, 
                 margin=.5, random_state=None):
  """Generates a synthetic data set composed of interlaced Archimedean spirals.

  Parameters
  ----------
  n_samples : int, default=500
      Total number of points equally divided among classes.
  n_classes : int, default=2
      Number of classes (i.e., spirals) to include in the dataset.
  shuffle : bool, default=True
      Shuffle the samples.
  noise : float, default=1
      Standard deviation of Gaussian noise added to the data.
  n_loops : float, default=2
      Number of loops of each spiral.
  margin : float, default=.5
      Margin separation between each spiral.
  random_state : int, RandomState instance or None, default=None
      Determines random number generation for dataset creation. Pass an int
      for reproducible output across multiple function calls.
  Returns
  -------
  X : ndarray of shape (n_samples, 1)
      The generated samples.
  y : ndarray of shape (n_samples,)
      The integer labels for class membership of each sample.
  """
  np.random.seed(random_state)
 
  n_samples_per_class = math.ceil(n_samples / n_classes)
  theta = np.random.rand(n_samples_per_class,1) * n_loops * 360 * np.pi / 180
 
  r = margin * n_classes * theta 
 
  X = np.array([]).reshape(0, 2)
  y = np.array([])
 
  for i in range(n_classes):
    rotated_theta = theta + i * 2 * np.pi / n_classes
    x1 = r * np.cos(rotated_theta) + np.random.rand(n_samples_per_class,1) * noise
    x2 = r * np.sin(rotated_theta) + np.random.rand(n_samples_per_class,1) * noise
    class_samples = np.hstack((x1, x2))
    X = np.vstack((X, class_samples))
    y = np.hstack((y, np.array([i]*n_samples_per_class)))
 
  if shuffle:
    X, y = utils.shuffle(X, y, random_state=random_state)

  X = X[0:n_samples,:]
  y = y[0:n_samples]
 
  return X, y
