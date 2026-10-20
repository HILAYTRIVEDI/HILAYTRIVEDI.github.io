# Gradient Boosting, XGBoost, LightGBM and CatBoost

> External reference: researched from public sources, not from the course.

## 1. Gradient boosting fundamentals

### 1.1 Boosting versus bagging

**One-line idea:** bagging averages many independent models to cut variance; boosting builds models one after another, each correcting the last, to cut bias.

| Aspect | Bagging (e.g. Random Forest) | Boosting (e.g. XGBoost) |
|---|---|---|
| Training | Parallel, independent trees | Sequential, each tree depends on earlier ones |
| Tree type | Deep, low-bias, high-variance | Shallow, weak learners |
| Main effect | Reduces variance | Reduces bias (and some variance with shrinkage) |
| Overfitting risk | Low, more trees rarely hurt | Higher, needs learning rate, early stopping |
| Tuning effort | Light | Heavier, but usually higher accuracy on tabular data |

### 1.2 Residual fitting intuition

**One-line idea:** each new tree predicts what the current ensemble still gets wrong.

Start with a constant prediction (the mean for squared error). Compute the residuals (actual minus predicted), fit a small tree to those residuals, add a scaled copy of its output to the prediction, and repeat. Every round nudges predictions towards the targets, like walking downhill in small steps.

### 1.3 Loss and gradient view

**One-line idea:** residuals are just the negative gradient of squared error, so boosting generalises to any differentiable loss.

The model is built stage-wise:

```
F_m(x) = F_(m-1)(x) + nu * h_m(x)
```

where `h_m` is a tree fitted to the negative gradient `-dL/dF` evaluated at `F_(m-1)`, and `nu` is the learning rate. For squared error, `-dL/dF = y - F`, which is the residual. For log loss, the "residual" is `y - p`, the gap between the label and the predicted probability. scikit-learn notes that each stage fits a regression tree to the negative gradient, even for classification.

Common losses: squared error, absolute error (robust to outliers), Huber, quantile (prediction intervals), log loss (classification), Poisson and gamma (counts and positive skewed targets).

### 1.4 What XGBoost adds: a regularised second-order objective

**One-line idea:** XGBoost uses both gradient `g` and Hessian `h`, and penalises tree complexity inside the objective.

```
obj = sum_i l(y_i, yhat_i) + sum_k omega(f_k)
omega(f) = gamma * T + 0.5 * lambda * sum_j w_j^2
```

`T` is the number of leaves and `w_j` the leaf scores. With `G_j` and `H_j` as the summed gradients and Hessians in leaf `j`:

```
optimal leaf weight  w_j* = -G_j / (H_j + lambda)
split gain = 0.5 * [G_L^2/(H_L+lambda) + G_R^2/(H_R+lambda) - (G_L+G_R)^2/(H_L+H_R+lambda)] - gamma
```

If the gain is negative, the split is not worth it (this acts as pruning). Because the solver only needs `g` and `h`, any twice-differentiable loss plugs in.

## 2. Core hyperparameters

### 2.1 Learning rate and number of trees

**One-line idea:** a small learning rate with many trees nearly always generalises better than a large rate with few.

Learning rate (`learning_rate` or `eta`) scales each tree's contribution. It trades off directly against `n_estimators`: halve one, roughly double the other. Practical recipe: fix `learning_rate` at 0.05 to 0.1, set a large `n_estimators`, and let early stopping choose the real number.

### 2.2 Tree depth and complexity

**One-line idea:** boosting wants weak, shallow trees; depth controls how many feature interactions the model can learn.

Depth `d` allows interactions of up to `d` features. Typical `max_depth` is 3 to 8. Stumps (depth 1) give a purely additive model. Deeper trees fit faster but overfit sooner.

### 2.3 Regularisation levers

**One-line idea:** limit what each tree may learn, or randomise what it sees.

| Lever | XGBoost | LightGBM | Effect |
|---|---|---|---|
| Min samples or hessian in leaf | `min_child_weight` (default 1) | `min_data_in_leaf`, `min_sum_hessian_in_leaf` | Stops tiny, noisy leaves |
| Min gain to split | `gamma` (default 0) | `min_gain_to_split` | Prunes weak splits |
| L2 on leaf values | `lambda` (default 1) | `lambda_l2` | Shrinks leaf scores |
| L1 on leaf values | `alpha` (default 0) | `lambda_l1` | Sparse leaf scores |
| Row subsampling | `subsample` | `bagging_fraction`, `bagging_freq` | Stochastic boosting, less variance |
| Column subsampling | `colsample_bytree` | `feature_fraction` | Decorrelates trees |

### 2.4 Key hyperparameter table with sensible starting values

| Parameter | Typical start | Notes |
|---|---|---|
| `learning_rate` | 0.05 to 0.1 | Lower is better, costs time |
| `max_depth` | 4 to 6 | XGBoost default 6 |
| `num_leaves` (LightGBM) | 31 | Keep below `2^max_depth` |
| `subsample` | 0.7 to 0.9 | Row sampling |
| `colsample_bytree` | 0.6 to 0.9 | Column sampling |
| `min_child_weight` / `min_data_in_leaf` | 1 to 20+ | Raise for noisy or large data |
| `lambda` | 1 to 10 | L2 |
| `n_estimators` | 1000+ | With early stopping |

### 2.5 Early stopping

**One-line idea:** stop adding trees when validation loss stops improving.

Hold out a validation set (or use cross-validation), monitor the metric, and stop after `k` rounds without improvement (`early_stopping_rounds`, or `n_iter_no_change` in scikit-learn). Use a validation set separate from the final test set, otherwise the test score is optimistic. In scikit-learn, `HistGradientBoosting*` enables early stopping by default when there are more than 10,000 samples.

## 3. Libraries compared

### 3.1 How each one differs

**One-line idea:** all three are gradient boosted trees; they differ in how trees grow, how features are binned and how categories are handled.

- **XGBoost:** level-wise (depth-wise) growth by default, regularised objective, histogram method (`tree_method='hist'`, now the `auto` default), sparse-aware, GPU support. Mature and widely supported.
- **LightGBM:** leaf-wise (best-first) growth, which converges faster but can overfit on small data unless `num_leaves` and `min_data_in_leaf` are controlled. Histogram binning and sampling tricks (GOSS, EFB) make it very fast on large data.
- **CatBoost:** symmetric (oblivious) trees, native categorical handling using ordered target statistics, and ordered boosting to reduce target leakage. Strong defaults, so it often works well with little tuning.

CatBoost's categorical encoding shuffles the rows and encodes each row's category using only the labels of rows that come earlier in the order, so a row's own label does not leak into its feature.

### 3.2 When to use which

| Situation | Pick | Why |
|---|---|---|
| General tabular baseline, need ecosystem and docs | XGBoost | Mature, stable, many integrations |
| Large dataset, many rows or features, speed matters | LightGBM | Fast training, low memory |
| Many high-cardinality categorical columns | CatBoost | Native ordered target encoding |
| Small data, little time to tune | CatBoost | Good defaults, less overfitting |
| Want zero extra dependencies | scikit-learn `HistGradientBoosting*` | Native NaN and categorical support |
| Need monotonic constraints | Any of them | All three support them (check the docs) |

### 3.3 Leaf-wise versus level-wise growth

**One-line idea:** level-wise grows every node at a depth; leaf-wise always splits the single leaf with the largest loss reduction.

Leaf-wise gives deeper, lopsided trees for the same leaf count, hence lower loss but more overfitting risk. LightGBM's docs advise keeping `num_leaves` below `2^max_depth` and raising `min_data_in_leaf` (hundreds or thousands on large data).

## 4. Practical workflow and code

### 4.1 XGBoost with early stopping

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBClassifier(
    n_estimators=2000,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    eval_metric="logloss",
    early_stopping_rounds=50,   # constructor argument in recent versions
    random_state=42,
)
model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
print(model.best_iteration)
```

Version-sensitive: in older XGBoost releases `early_stopping_rounds` was passed to `fit()`; in 2.x it belongs in the constructor. Check the docs for your installed version.

### 4.2 LightGBM

```python
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=2000, learning_rate=0.05,
    num_leaves=31, min_child_samples=20,
    subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
)
model.fit(
    X_tr, y_tr, eval_set=[(X_val, y_val)],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
)
```

Version-sensitive: LightGBM moved from an `early_stopping_rounds` argument to the `lgb.early_stopping` callback. Parameter aliases (`min_child_samples` is `min_data_in_leaf`) also vary.

### 4.3 CatBoost with categorical columns

```python
from catboost import CatBoostClassifier

cat_cols = ["city", "device"]          # column names or indices
model = CatBoostClassifier(iterations=2000, learning_rate=0.05, depth=6, verbose=0)
model.fit(X_tr, y_tr, cat_features=cat_cols,
          eval_set=(X_val, y_val), early_stopping_rounds=50)
```

### 4.4 scikit-learn native option

```python
from sklearn.ensemble import HistGradientBoostingClassifier

clf = HistGradientBoostingClassifier(
    learning_rate=0.1, max_leaf_nodes=31,
    categorical_features="from_dtype",   # needs pandas category dtype
    early_stopping=True,
)
clf.fit(X_tr, y_tr)
```

It bins features into up to 256 bins, handles missing values natively and supports monotonic and interaction constraints.

### 4.5 Suggested tuning order

1. Fix `learning_rate` (0.05 to 0.1) and use early stopping to find the tree count.
2. Tune depth or `num_leaves` and `min_child_weight` or `min_data_in_leaf`.
3. Tune `subsample` and `colsample_bytree`.
4. Tune `lambda`, `alpha`, `gamma`.
5. Lower the learning rate at the end and refit.

Use random search or a tool such as Optuna rather than a full grid.

## 5. Feature importance and explanation

### 5.1 Built-in importance and its limits

**One-line idea:** gain, split-count and cover importances are cheap but biased and training-set based.

scikit-learn warns that impurity-based importance is computed from training statistics, favours high-cardinality features and may not reflect predictive value on held-out data. It recommends `sklearn.inspection.permutation_importance` instead.

### 5.2 SHAP pointer

**One-line idea:** SHAP gives each feature a signed contribution per prediction, based on Shapley values from game theory.

`shap.TreeExplainer` computes exact, fast SHAP values for XGBoost, LightGBM, CatBoost and scikit-learn trees. Use summary plots for global importance and force or waterfall plots for single predictions. Reference: the SHAP documentation and Lundberg et al. (2020), "From local explanations to global understanding with explainable AI for trees". SHAP explains the model, not causality. Correlated features share credit.

## 6. Use cases

- Credit scoring, fraud detection, churn prediction (tabular, imbalanced, mixed types).
- Ranking and search relevance (LambdaRank objectives in XGBoost and LightGBM).
- Demand and sales forecasting using lag features (regression with engineered features).
- Insurance claims with Poisson or gamma objectives.
- Kaggle-style tabular competitions: gradient boosting is a standard first choice.
- Not ideal for images, raw text or audio: neural networks usually win there.

## 7. Common mistakes

- Tuning on the test set, or using the test set for early stopping.
- High learning rate with no early stopping, then blaming the algorithm for overfitting.
- Leaving `num_leaves` large in LightGBM on small data.
- One-hot encoding high-cardinality categories when the library handles them natively.
- Scaling features: not needed for tree models.
- Ignoring class imbalance (`scale_pos_weight`, class weights, or the right metric such as PR-AUC).
- Trusting default feature importance blindly.
- Random splits on time series data (leaks the future); use time-based splits.
- Target leakage through features that encode the label.

## Quick revision cheat sheet

- Bagging reduces variance (parallel, deep trees). Boosting reduces bias (sequential, shallow trees).
- Each tree fits the negative gradient of the loss; for squared error that is the residual.
- Update rule: `F_m = F_(m-1) + nu * h_m`.
- XGBoost: second-order, regularised: `w* = -G/(H+lambda)`, gain minus `gamma`.
- Learning rate down, trees up, use early stopping on a separate validation set.
- Depth 3 to 8 for XGBoost; `num_leaves` below `2^max_depth` for LightGBM.
- Regularise with `min_child_weight`, `gamma`, `lambda`, `alpha`, `subsample`, `colsample_bytree`.
- XGBoost: safe default. LightGBM: big data, speed. CatBoost: categoricals, small data, good defaults.
- Prefer SHAP or permutation importance over built-in impurity importance.
- No scaling needed. Library APIs (early stopping arguments, callbacks) are version-sensitive.

## Sources

- XGBoost parameters: https://xgboost.readthedocs.io/en/stable/parameter.html
- XGBoost, introduction to boosted trees: https://xgboost.readthedocs.io/en/stable/tutorials/model.html
- LightGBM parameters tuning: https://lightgbm.readthedocs.io/en/stable/Parameters-Tuning.html
- CatBoost, transforming categorical features to numerical: https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic
- scikit-learn ensembles, gradient boosting: https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
- Background (cited from knowledge, not fetched): Friedman (2001), "Greedy function approximation: a gradient boosting machine"; Chen and Guestrin (2016), "XGBoost: a scalable tree boosting system"; Ke et al. (2017), LightGBM; Prokhorenkova et al. (2018), CatBoost.
