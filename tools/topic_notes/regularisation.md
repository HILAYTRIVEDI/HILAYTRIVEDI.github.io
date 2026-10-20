# Regularisation

> External reference: researched from public sources, not from the course.

## 1. The core idea

### 1.1 What regularisation is

**One line:** add a penalty on model complexity to the loss, so the model cannot fit noise by using huge weights.

Intuition: an unregularised model chases every wiggle in the training data. The penalty makes large coefficients expensive, so the model keeps only the weights the data strongly justifies.

Training objective: `minimise  loss(data) + lambda * complexity(weights)`

Google's ML Crash Course calls lambda the regularisation rate. scikit-learn calls the same knob `alpha` (for linear models) or `C` (for `LogisticRegression` and SVMs, where `C` is roughly `1/alpha`, so a small `C` means strong regularisation).

### 1.2 Why it works: bias and variance

**One line:** regularisation deliberately adds a little bias to remove a lot of variance.

| Strength of penalty | Weights | Bias | Variance | Typical symptom |
|---|---|---|---|---|
| Zero (lambda = 0) | Free, can be huge | Lowest | Highest | Overfitting: train score high, validation score low |
| Moderate | Shrunk | Slightly higher | Much lower | Best validation score |
| Very strong | Near zero | High | Low | Underfitting: both scores poor |

Intuition: with many features or collinear features, ordinary least squares coefficients become unstable (small data changes cause big swings). Shrinking them stabilises predictions. Test error as a function of alpha is usually U-shaped, and the aim is the bottom of the U.

Features must be on a comparable scale (use `StandardScaler`) because the penalty treats all weights equally. Do not penalise the intercept (scikit-learn already leaves it out).

## 2. L2, L1 and ElasticNet

### 2.1 Ridge (L2)

**One line:** penalise the sum of squared weights; weights shrink smoothly but almost never reach exactly zero.

scikit-learn objective: `min_w ||Xw - y||^2 + alpha * ||w||_2^2`

- Keeps every feature in the model.
- Handles collinearity well: correlated features share weight.
- Has a closed-form solution, so it is fast and stable.
- Google's crash course notes L2 "never pushes weights all the way to zero".

### 2.2 Lasso (L1)

**One line:** penalise the sum of absolute weights; some weights become exactly zero, so it selects features.

scikit-learn objective: `min_w (1 / (2n)) ||Xw - y||^2 + alpha * ||w||_1`

- Produces sparse, easier-to-interpret models.
- With a group of correlated features it tends to keep one more or less arbitrarily and drop the rest, so the chosen set can be unstable between resamples.
- Solved by coordinate descent (`Lasso`) or LARS (`LassoLars`).

Note the scaling difference: scikit-learn's Ridge uses the plain sum of squares while Lasso and ElasticNet divide the data term by `2n`. The same numeric `alpha` therefore does not mean the same strength across the two.

### 2.3 ElasticNet (L1 + L2)

**One line:** a weighted mix of both penalties, giving sparsity and stability together.

`min_w (1 / (2n)) ||Xw - y||^2 + alpha * rho * ||w||_1 + (alpha * (1 - rho) / 2) * ||w||_2^2`

`rho` is `l1_ratio`: 1 gives Lasso, near 0 gives Ridge-like behaviour. scikit-learn's guidance is that ElasticNet tends to keep whole groups of correlated features, where Lasso picks one.

### 2.4 Geometry: why L1 gives zeros and L2 does not

**One line:** the constrained form of each penalty is a region around the origin, and the loss contours first touch it at a corner (L1) or a smooth curve (L2).

Equivalent view: minimise the loss subject to `||w||_1 <= t` (Lasso) or `||w||_2^2 <= t` (Ridge). In two dimensions:

| | L2 (Ridge) | L1 (Lasso) |
|---|---|---|
| Constraint region | Circle (sphere in higher dimensions) | Diamond with corners on the axes |
| Where elliptical loss contours touch it | Almost anywhere on the smooth boundary, so both weights are non-zero | Often at a corner, where one weight is exactly zero |
| Gradient of penalty | `2w`, shrinks toward zero as `w` shrinks, so the pull fades | `sign(w)`, constant pull, so a small weight is driven all the way to zero |

Intuition for the gradient row: L2 pulls a weight in proportion to its size, so tiny weights barely feel it. L1 pulls with constant force, so it can finish the job and hit zero. In high dimensions the L1 region has many corners and edges on the axes, hence many zero coefficients. (This is the standard treatment in Hastie, Tibshirani and Friedman, The Elements of Statistical Learning, chapter 3; the geometry here is general knowledge, not taken from a page I fetched.)

### 2.5 Bayesian view (brief, general knowledge)

Ridge equals maximum a posteriori estimation with a Gaussian prior on the weights. Lasso equals MAP with a Laplace prior, which is sharply peaked at zero and so favours exact zeros.

## 3. Choosing alpha

### 3.1 Use cross-validation

**One line:** pick the alpha that gives the best average validation score on held-out folds, never the training score.

Intuition: training error always falls as alpha falls, so only held-out data can find the bottom of the U.

- Search on a log scale, for example `np.logspace(-4, 3, 30)`.
- `RidgeCV`: efficient leave-one-out by default; set `cv=` for k-fold. With the default LOO, alpha cannot be 0.
- `LassoCV`: cross-validates along a path of alphas. scikit-learn says it is usually preferable for high-dimensional data with many collinear features.
- `LassoLarsCV`: often faster than `LassoCV` when samples are few relative to features.
- `ElasticNetCV`: tunes both `alpha` and `l1_ratio`.
- Fit the scaler inside a `Pipeline` so each CV fold scales using only its training part (avoids leakage).
- Optional "one-standard-error rule" (general knowledge): choose the strongest alpha whose score is within one standard error of the best, for a simpler model.

### 3.2 Worked sklearn example

Version note: `RidgeCV`, `LassoCV`, `ElasticNetCV` have been stable for years, but parameter defaults can change between releases. Check the docs for your installed version.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.metrics import root_mean_squared_error

X, y = make_regression(n_samples=200, n_features=50, n_informative=8,
                       noise=15, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)

alphas = np.logspace(-3, 3, 40)
models = {
    "ridge":   make_pipeline(StandardScaler(), RidgeCV(alphas=alphas, cv=5)),
    "lasso":   make_pipeline(StandardScaler(), LassoCV(cv=5, random_state=0)),
    "elastic": make_pipeline(StandardScaler(),
                             ElasticNetCV(l1_ratio=[.2, .5, .8, 1], cv=5,
                                          random_state=0)),
}
for name, m in models.items():
    m.fit(X_tr, y_tr)
    est = m[-1]
    nonzero = int(np.sum(est.coef_ != 0))
    print(name, "alpha=%.4f" % est.alpha_, "nonzero=%d" % nonzero,
          "test RMSE=%.2f" % root_mean_squared_error(y_te, m.predict(X_te)))
```

Expected pattern: Lasso and ElasticNet report far fewer non-zero coefficients than Ridge (which keeps all 50).

For classification, `LogisticRegression(penalty="l1", solver="saga", C=0.5)` or `penalty="l2"`; smaller `C` means stronger regularisation. (The `penalty` argument has been changing in recent scikit-learn versions, so check your version.)

## 4. Regularisation beyond linear models

### 4.1 Early stopping

**One line:** stop training when validation loss starts rising, before the model fully converges.

Intuition: weights start small and grow during training, so stopping early limits effective complexity without computing a penalty. Google's crash course calls it quick but rarely optimal; it usually raises training loss while lowering test loss. Available in Keras (`EarlyStopping(patience=...)`), gradient boosting (`n_iter_no_change`) and `MLPClassifier(early_stopping=True)`.

### 4.2 Dropout

**One line:** randomly switch off units during each training step so no unit can rely on specific others.

Intuition: Srivastava et al. (JMLR 2014) describe each training pass as sampling a different "thinned" network, preventing co-adaptation of units. At test time one full network with scaled weights approximates averaging all the thinned networks. It is a neural-network technique, off at inference.

```python
from tensorflow import keras
model = keras.Sequential([
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.3),      # 30% of units dropped per step during training
    keras.layers.Dense(1, activation="sigmoid"),
])
```

### 4.3 Other forms (names only)

Weight decay (L2 in neural-network optimisers), data augmentation, smaller model, pruning trees (`max_depth`, `ccp_alpha`), `min_samples_leaf`, more data. All trade a little bias for lower variance.

## 5. When to use which

### 5.1 Decision table

| Situation | Choose | Reason |
|---|---|---|
| Many features, all probably useful, collinear | Ridge | Shrinks without dropping; stable under collinearity |
| Many features, you believe only a few matter | Lasso | Sparse model, built-in feature selection |
| Correlated feature groups and you want sparsity | ElasticNet | Keeps groups, still zeroes noise |
| More features than samples (p > n) | ElasticNet or Ridge | Lasso selects at most n features |
| Need an interpretable short list of drivers | Lasso (then check stability) | Exact zeros |
| Neural network overfitting | Dropout, weight decay, early stopping | Standard tools for deep models |
| Boosted trees overfitting | Early stopping, shrinkage (learning rate), depth limits | Tree-specific controls |
| Unsure | ElasticNetCV | Covers both ends via `l1_ratio` |

### 5.2 Use cases

| Domain | Example | Typical choice |
|---|---|---|
| Genomics and text | Thousands of gene or word features, few samples | Lasso or ElasticNet |
| Finance and economics | Collinear indicators predicting returns | Ridge |
| House prices | Dozens of overlapping size and location features | Ridge or ElasticNet |
| Click-through and ad models | Millions of sparse features | L1 logistic regression for sparsity |
| Polynomial regression | High-degree terms | Ridge to tame the wiggle |
| Image and NLP deep nets | Overparameterised networks | Dropout, weight decay, early stopping |

## 6. Common mistakes

### 6.1 Checklist

- Forgetting to scale features, so the penalty hits large-scale features unfairly.
- Choosing alpha on the training or test set instead of CV (leaks the test set).
- Scaling before the CV split (leakage); use a `Pipeline`.
- Reading Lasso's chosen features as "the true causes". With correlated features the selection is arbitrary and unstable.
- Assuming the same numeric alpha means the same strength across Ridge and Lasso (different scaling in scikit-learn).
- Confusing `alpha` (higher means stronger) with `C` (higher means weaker).
- Searching alpha on a linear grid instead of a log grid.
- Applying dropout at inference time.
- Regularising an already underfitting model; first check the learning curves.
- Interpreting coefficients as unbiased effects. Shrinkage biases them toward zero by design.

## Quick revision cheat sheet

- Regularisation: `loss + lambda * complexity`; trades small bias for big variance reduction.
- Ridge (L2): squared weights; shrinks, never exactly zero; best for collinearity.
- Lasso (L1): absolute weights; exact zeros; feature selection; unstable among correlated features.
- ElasticNet: mix via `l1_ratio`; keeps correlated groups, still sparse.
- Geometry: L2 region is a circle, L1 is a diamond with corners on the axes, so contours hit corners and give zeros.
- Gradient view: L2 pull fades with weight size, L1 pull is constant.
- Choose alpha by CV on a log grid (`RidgeCV`, `LassoCV`, `ElasticNetCV`); scale features inside a pipeline.
- `C` in logistic regression and SVM is the inverse of regularisation strength.
- Early stopping: halt when validation loss rises. Dropout: random unit removal in training only.
- Too much regularisation means underfitting (high bias); too little means overfitting (high variance).

## Sources

- https://scikit-learn.org/stable/modules/linear_model.html (Ridge, Lasso, ElasticNet objectives, CV variants, correlated-feature guidance)
- https://developers.google.com/machine-learning/crash-course/overfitting/regularization (L2, lambda, early stopping)
- https://jmlr.org/papers/v15/srivastava14a.html (Dropout paper abstract)
- https://hastie.su.domains/ElemStatLearn/ (ESL book homepage; geometry and Bayesian points are general knowledge consistent with its chapter 3)
