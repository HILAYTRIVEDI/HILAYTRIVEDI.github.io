# Evaluation Metrics for Classification and Regression

> External reference: researched from public sources, not from the course.

## 1. Classification basics

### 1.1 Confusion matrix

**One line:** a table counting how predictions line up with the truth, from which most metrics are derived.

|  | Predicted positive | Predicted negative |
|---|---|---|
| **Actually positive** | TP (true positive) | FN (false negative, a miss) |
| **Actually negative** | FP (false positive, a false alarm) | TN (true negative) |

Intuition: always look at this table first. A single number hides which kind of error the model makes, and the two errors usually have different costs.

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_true, y_pred)       # rows = true, columns = predicted
tn, fp, fn, tp = cm.ravel()                 # binary case
```

### 1.2 Accuracy

**One line:** the share of all predictions that were correct.

`accuracy = (TP + TN) / (TP + TN + FP + FN)`

Fine for balanced classes with equal error costs. Misleading otherwise: Google's crash course gives the example of a model that always predicts negative on data with 1% positives, scoring 99% while detecting nothing.

### 1.3 Precision and recall

**One line:** precision asks "when I say positive, how often am I right?"; recall asks "of all real positives, how many did I find?"

- `precision = TP / (TP + FP)`
- `recall = TP / (TP + FN)` (also called sensitivity or true positive rate)

Intuition: precision punishes false alarms, recall punishes misses. Neither uses TN, so a huge negative class cannot inflate them.

### 1.4 F1 and F-beta

**One line:** F1 is the harmonic mean of precision and recall; it is low unless both are reasonably high.

- `F1 = 2PR / (P + R) = 2TP / (2TP + FP + FN)`
- `F_beta = (1 + beta^2) TP / ((1 + beta^2) TP + FP + beta^2 FN)`; beta > 1 favours recall (F2), beta < 1 favours precision (F0.5).

Caveats from scikit-learn: F is undefined when there are no TP, FP or FN (control with `zero_division`); F1 ignores TN; macro-F is the mean of per-class F values, not the harmonic mean of macro precision and macro recall.

### 1.5 Other confusion-matrix metrics

| Metric | Formula | Use |
|---|---|---|
| Specificity (TNR) | TN / (TN + FP) | How well negatives are cleared |
| False positive rate | FP / (FP + TN) = 1 - specificity | x-axis of the ROC curve |
| Balanced accuracy | mean of per-class recall | Accuracy that is fair under imbalance (a majority-class predictor drops toward 1/n_classes) |
| MCC (Matthews correlation) | (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) | Single balanced score from -1 to +1, robust to imbalance |
| Cohen's kappa | agreement beyond chance | Annotator agreement, imbalanced labels |

### 1.6 Multiclass averaging

**One line:** for more than two classes, compute per-class scores then average them in a chosen way.

| `average=` | Meaning | Use when |
|---|---|---|
| `micro` | Pool TP, FP, FN over all classes (equals accuracy for single-label data) | You care about overall per-sample performance |
| `macro` | Plain mean over classes | All classes matter equally, rare ones included |
| `weighted` | Mean weighted by class size | You want a size-aware summary |
| `None` | One score per class | Diagnosing which class fails |

## 2. Threshold-free and probability metrics

### 2.1 Threshold choice

**One line:** most classifiers output a score; the 0.5 cut-off is a default, not a law.

Raising the threshold gives fewer false positives and more false negatives; lowering it does the opposite. So precision and recall usually move in opposite directions (Google ML Crash Course). Pick the threshold from the business cost, then verify on held-out data.

Ways to choose:

- Minimise expected cost: `cost = c_FP * FP + c_FN * FN` over candidate thresholds.
- Fix a requirement ("recall at least 95%") and take the highest precision meeting it.
- Maximise F1 (or F-beta) on a validation set.
- Youden's J (`TPR - FPR`) for a balanced operating point on the ROC curve.

```python
from sklearn.metrics import precision_recall_curve
import numpy as np
p, r, t = precision_recall_curve(y_val, scores)
f1 = 2 * p[:-1] * r[:-1] / (p[:-1] + r[:-1] + 1e-12)
best_t = t[np.argmax(f1)]
y_pred = (scores >= best_t).astype(int)
```

Choose the threshold on a validation set, not the test set, and recheck it if class prevalence changes.

### 2.2 ROC curve and ROC-AUC

**One line:** ROC plots true positive rate against false positive rate across all thresholds; AUC is the area under it.

Intuition: AUC equals the probability that a random positive is scored above a random negative. 0.5 is random ranking, 1.0 is perfect. It judges ranking quality independent of any threshold. Pass probabilities or decision scores, never hard labels.

```python
from sklearn.metrics import roc_auc_score
roc_auc_score(y_true, model.predict_proba(X)[:, 1])
# multiclass: roc_auc_score(y, proba, multi_class="ovr", average="macro")
```

Caveat: with heavy imbalance, FPR is diluted by the large negative count, so ROC-AUC can look optimistic while the model still produces many false alarms in absolute terms.

### 2.3 Precision-recall curve and PR-AUC (average precision)

**One line:** the PR curve plots precision against recall across thresholds and focuses entirely on the positive class.

- `AP = sum_n (R_n - R_{n-1}) * P_n`, computed by `average_precision_score`.
- The chance baseline is the positive-class prevalence, not 0.5, so values are not comparable across datasets with different class balance.
- scikit-learn warns that linear interpolation (trapezoidal `auc` on the PR curve) can be overly optimistic; prefer `average_precision_score` and say which one you report.
- With few positives the curve is jagged and noisy.

Rule of thumb: rare positives and you care about finding them, so prefer PR-AUC; roughly balanced classes or you care about both classes, ROC-AUC is fine.

### 2.4 Log loss (cross-entropy)

**One line:** measures the quality of predicted probabilities, punishing confident wrong answers very heavily.

Binary: `-(1/N) * sum [ y*log(p) + (1-y)*log(1-p) ]`. Lower is better; it needs `predict_proba` output.

Intuition: predicting 0.99 for something that turns out negative costs far more than predicting 0.6. Use it when probabilities themselves are used (risk scores, expected-value decisions), together with a calibration check (`CalibrationDisplay`, Brier score). AUC can be high while probabilities are badly calibrated.

```python
from sklearn.metrics import log_loss
log_loss([0, 0, 1, 1], [[.9, .1], [.8, .2], [.3, .7], [.01, .99]])   # 0.1738
```

## 3. Regression metrics

### 3.1 MAE, MSE, RMSE

**One line:** average size of the errors, measured in absolute terms (MAE) or squared terms (MSE, RMSE).

| Metric | Formula | Property |
|---|---|---|
| MAE | `mean(abs(y - y_hat))` | Same units as y; robust to outliers; targets the median |
| MSE | `mean((y - y_hat)^2)` | Penalises large errors strongly; targets the mean; smooth to optimise |
| RMSE | `sqrt(MSE)` | Same units as y; still outlier-sensitive |

Intuition: RMSE is always at least MAE. A large gap between them signals a few big errors. All three depend on the units of y, so you cannot compare them across different targets.

### 3.2 R-squared

**One line:** the fraction of the target's variance explained, relative to a model that always predicts the mean.

`R2 = 1 - SS_res / SS_tot`

- 1 is perfect, 0 equals the mean baseline, and it can be negative on test data (worse than the mean).
- On training data, R2 never falls when you add features. Use adjusted R2 or, better, test or CV R2.
- It ranks models identically to MSE on the same data but says nothing about whether predictions are accurate enough in real units.

### 3.3 Other regression metrics (brief)

| Metric | Use |
|---|---|
| MAPE or sMAPE | Percentage error; breaks when true values are near zero |
| RMSLE (`root_mean_squared_log_error`) | Targets spanning orders of magnitude; penalises under-prediction more |
| Median absolute error | Very robust to outliers |
| Pinball loss | Quantile forecasts and prediction intervals |
| Poisson or Gamma deviance | Count and positive-skewed targets |

scikit-learn scorers follow "higher is better", so error metrics appear as `neg_mean_absolute_error`, `neg_root_mean_squared_error` and so on in `cross_val_score` and `GridSearchCV`. Version note: `root_mean_squared_error` as a function exists only in newer scikit-learn releases; older ones use `mean_squared_error(..., squared=False)`.

## 4. When to use which

### 4.1 Classification

| Situation | Prefer | Avoid or caution |
|---|---|---|
| Balanced classes, equal costs | Accuracy, F1 | None in particular |
| Rare positives, misses are costly (disease, fraud) | Recall, F2, PR-AUC | Accuracy |
| False alarms are costly (spam filter, content takedown) | Precision, F0.5 | Recall alone |
| Need one score under imbalance | Balanced accuracy, MCC, PR-AUC | Plain accuracy |
| Ranking quality independent of threshold | ROC-AUC (balanced) or PR-AUC (imbalanced) | Threshold metrics at the default 0.5 |
| Probabilities are used downstream | Log loss, Brier score, calibration plot | AUC alone |
| Multiclass, rare classes matter | Macro-F1, per-class report | Micro (hides rare classes) |
| Multiclass, overall volume matters | Micro or weighted | Macro (over-weights tiny classes) |

### 4.2 Regression

| Situation | Prefer | Reason |
|---|---|---|
| Large errors are disproportionately bad | RMSE or MSE | Squaring emphasises them |
| Outliers in the target are noise | MAE or median absolute error | Robust |
| Need a unit-free comparison | R2, MAPE (if y is far from 0) | Scale independent |
| Multiplicative errors, wide range | RMSLE | Log scale |
| Prediction intervals | Pinball loss | Quantile-aware |

## 5. Use cases

| Domain | Positive class | Metric emphasis | Why |
|---|---|---|---|
| Cancer screening | Disease | High recall, then precision via follow-up tests | A miss is far worse than a retest |
| Fraud detection | Fraud | PR-AUC, recall at fixed precision | Very rare positives; review capacity is limited |
| Spam filtering | Spam | Precision | Losing a genuine email is costly |
| Credit scoring | Default | ROC-AUC or KS for ranking, log loss for pricing | Probabilities set interest rates |
| Search and recommendation | Relevant item | Precision at k, recall at k, average precision | Only the top results are seen |
| House price or demand forecast | Not applicable | RMSE or MAE in real units, plus R2 | Business reads errors in rupees or units |
| Delivery time estimate | Not applicable | MAE, quantile loss | Median and tail behaviour matter |

## 6. Common mistakes

### 6.1 Checklist

- Reporting accuracy on imbalanced data.
- Computing AUC from hard labels instead of scores.
- Tuning the threshold on the test set.
- Comparing PR-AUC across datasets with different prevalence.
- Using ROC-AUC as the only metric when negatives vastly outnumber positives.
- Using micro-F1 and believing it reflects rare-class performance.
- Reporting training-set metrics, or R2 on training data.
- Data leakage: preprocessing or resampling before the train/test split. Oversample only inside the training fold.
- Using MAPE when the target can be zero or near zero.
- Comparing RMSE across targets with different units.
- Ignoring uncertainty: report a CV mean and spread, or a confidence interval, not one lucky split.
- Optimising a metric that does not match the business cost.
- Ignoring calibration when probabilities drive decisions.
- Ignoring distribution shift: metrics measured on old data may not hold in production.

## Quick revision cheat sheet

- Confusion matrix: TP, FP, FN, TN. Start here.
- Accuracy = (TP+TN)/all. Only safe when balanced.
- Precision = TP/(TP+FP). Recall = TP/(TP+FN). Opposite directions as the threshold moves.
- F1 = harmonic mean of P and R; F-beta weights recall when beta > 1.
- Specificity = TN/(TN+FP); FPR = 1 - specificity.
- Balanced accuracy and MCC handle imbalance in one number.
- ROC-AUC = P(random positive scored above random negative); 0.5 is random. Can flatter on heavy imbalance.
- PR-AUC (average precision): baseline is the prevalence; best for rare positives.
- Log loss: probability quality, punishes confident errors; check calibration.
- Threshold: set by cost or by a recall or precision requirement, on validation data.
- MAE: robust, median-like. RMSE: punishes big errors. R2: variance explained, can be negative on test data.
- Multiclass: macro = rare classes count; micro = overall volume; weighted = size-aware.
- Always match the metric to the real cost of each error type.

## Sources

- https://scikit-learn.org/stable/modules/model_evaluation.html (metric definitions, averaging, balanced accuracy, MCC, average precision, log loss, scoring conventions)
- https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall (accuracy, precision, recall, imbalance, threshold trade-off)
- https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html (PR curves, prevalence baseline, imbalance caveats)
