# PCA and Dimensionality Reduction (with t-SNE and UMAP)

> External reference: researched from public sources, not from the course.

## 1. Principal Component Analysis

### 1.1 What PCA does

**One-line idea:** PCA rotates the data onto new orthogonal axes (principal components) ordered by how much variance they capture, so you can keep only the first few.

Intuition: imagine a cloud of points shaped like a cigar. The first component runs along the cigar's length (most spread), the second is perpendicular to it, and so on. Dropping the later axes loses little information if the cloud is nearly flat in those directions. PCA is linear and unsupervised: it never sees the labels.

### 1.2 The maths in brief

**One-line idea:** components are the eigenvectors of the covariance matrix; eigenvalues are the variances along them.

1. Centre the data: subtract each feature's mean to get `X`.
2. Covariance: `C = X^T X / (n - 1)`.
3. Eigen-decompose `C = V Lambda V^T`. Columns of `V` are the components, `lambda_k` is the variance along component `k`.
4. Project: `Z = X V_k`, using the first `k` columns.

### 1.3 Link to SVD

**One-line idea:** the SVD of the centred data gives PCA directly, and is how libraries compute it.

```
X = U S V^T
```

The columns of `V` are the principal directions. The eigenvalues of the covariance matrix are `s_i^2 / (n - 1)`. The scores are `U S`. SVD is numerically more stable than forming `X^T X`, and scikit-learn's `PCA` centres the data (but does not scale it) and then applies SVD. Randomised SVD (`svd_solver='randomized'`) is efficient when you keep few components; the inverse transform is then approximate.

### 1.4 Explained variance

**One-line idea:** each component's share of total variance tells you how much information it carries.

```
explained variance ratio_k = lambda_k / sum(lambda)
```

Choose `k` so that the cumulative ratio reaches a target such as 90% to 95%. In scikit-learn, `PCA(n_components=0.95)` picks the smallest `k` meeting that fraction (documented in the API reference, not in the user guide page consulted).

### 1.5 Scree plot

**One-line idea:** plot the variance per component and look for the elbow where the curve flattens.

Components before the elbow carry signal; those after mostly carry noise. Pair it with the cumulative variance curve. The elbow is a judgement call, so also consider downstream performance (cross-validate the model with different `k`) rather than relying on the plot alone.

### 1.6 Scaling matters

**One-line idea:** PCA maximises variance, so a feature with a large scale dominates unless you standardise.

PCA centres but does not scale. If features are in different units (income in lakhs, age in years), standardise first with `StandardScaler`. This is PCA on the correlation matrix. Skip scaling only when features share a meaningful common unit (for example pixel intensities). Fit the scaler and PCA on training data only, then apply to test data, ideally inside a `Pipeline`.

### 1.7 Code

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

pipe = make_pipeline(StandardScaler(), PCA())
pipe.fit(X_train)
pca = pipe.named_steps["pca"]

ratio = pca.explained_variance_ratio_
plt.plot(range(1, len(ratio) + 1), ratio, "o-", label="per component")   # scree plot
plt.plot(range(1, len(ratio) + 1), np.cumsum(ratio), "s--", label="cumulative")
plt.xlabel("Component"); plt.ylabel("Explained variance ratio"); plt.legend(); plt.show()

# keep enough components for 95% of the variance
pipe95 = make_pipeline(StandardScaler(), PCA(n_components=0.95))
X_train_p = pipe95.fit_transform(X_train)
X_test_p = pipe95.transform(X_test)
print(pipe95.named_steps["pca"].n_components_)
```

Version-sensitive: scikit-learn's `svd_solver` defaults and parameter handling change between releases. Check the docs for your installed version.

### 1.8 PCA variants

| Variant | Use when |
|---|---|
| `IncrementalPCA` | Data does not fit in memory; use `partial_fit` on chunks |
| `KernelPCA` | Structure is non-linear (RBF or other kernels); components bounded by sample count |
| `TruncatedSVD` | Sparse data such as TF-IDF (no centring, so sparsity is kept) |
| `PCA(whiten=True)` | Downstream model assumes unit-variance, uncorrelated inputs (RBF SVM, K-Means) |

## 2. Non-linear methods for visualisation

### 2.1 t-SNE

**One-line idea:** t-SNE places points in 2D or 3D so that near neighbours stay near, making local clusters visible.

It turns pairwise distances into probabilities and minimises the KL divergence between the high- and low-dimensional versions using a Student-t distribution in the embedding. Key points from the scikit-learn docs:

- `perplexity` roughly sets how many neighbours matter. Small values focus on very local structure; larger values suit bigger or noisier data. Try several.
- The cost is not convex, so results depend on the seed. Use `init='pca'` for more stable global layout.
- Barnes-Hut costs about `O(N log N)`, with a maximum of 3 output dimensions. Exact is `O(N^2)`.
- Scale features first. Consider reducing to 30 to 50 dimensions with PCA before t-SNE for speed and noise reduction.

```python
from sklearn.manifold import TSNE

emb = TSNE(n_components=2, perplexity=30, init="pca",
           learning_rate="auto", random_state=0).fit_transform(X_scaled)
```

What not to infer: distances between clusters, relative cluster sizes and density are not reliable. Visible clusters can appear even when the true structure is continuous. t-SNE has no `transform` for new data in scikit-learn.

### 2.2 UMAP

**One-line idea:** UMAP builds a neighbourhood graph and finds a low-dimensional layout of it, usually faster than t-SNE and with somewhat better global structure.

Parameters from the UMAP docs:

- `n_neighbors` (default 15): small gives fine local detail but fragments; large captures broad structure.
- `min_dist` (default 0.1): small gives tight clumps (good for clustering); large spreads points out.
- `n_components`: unlike t-SNE, UMAP scales to higher output dimensions (10 to 50 can feed clustering or models).
- `metric`: euclidean, cosine, hamming and others.

```python
import umap   # pip install umap-learn

emb = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2,
                random_state=42).fit_transform(X_scaled)
```

UMAP can `transform` new points. The `umap-learn` API is version-sensitive. Setting `random_state` improves reproducibility but disables some parallelism. Like t-SNE, the layout is still a heuristic: do not over-read distances between clusters.

### 2.3 When to use which

| Goal | Method | Why |
|---|---|---|
| Preprocessing for a model, denoising, speed | PCA | Linear, fast, invertible, has `transform` |
| Understand how much variance is captured | PCA | Explained variance, scree plot |
| Decorrelate features (multicollinearity) | PCA | Components are orthogonal |
| Look at local cluster structure in 2D | t-SNE | Strong local separation |
| Visualise large data, keep some global layout, embed new points | UMAP | Faster, has `transform` |
| Sparse text vectors | TruncatedSVD | Keeps sparsity |
| Non-linear manifold, moderate size | KernelPCA | Kernel trick |
| Features for clustering in 10 to 50 dimensions | PCA or UMAP | Both can feed clustering |

## 3. When not to use these methods

- **PCA:** when interpretability of original features matters (components are mixtures); when the signal lies in low-variance directions (variance is not relevance); when relationships are strongly non-linear; for categorical data without proper encoding; before tree models, which gain little from it.
- **t-SNE and UMAP:** as model inputs for production pipelines (t-SNE especially); for quantitative claims about distances or cluster sizes; to prove that classes are or are not separable (a messy 2D plot does not mean a supervised model will fail).
- **Any method:** when the number of features is already small and the model is fast. Reduction adds complexity and loses information.
- **Supervised tasks:** PCA ignores labels. If you want directions that separate classes, consider LDA or just let a regularised model select features.

## 4. Use cases

- Compressing high-dimensional features (images, spectra, sensor data) before a classifier.
- Removing multicollinearity before linear or logistic regression.
- Noise reduction: reconstruct from the top `k` components.
- Visualising embeddings (word, image or customer embeddings) with t-SNE or UMAP.
- Exploratory analysis of single-cell or genomics data (PCA then UMAP is a standard workflow).
- Anomaly detection through reconstruction error.
- Speeding up K-Means or nearest-neighbour search in high dimensions.

## 5. Common mistakes

- Forgetting to scale features of different units.
- Fitting PCA on the full dataset before the train-test split (leakage). Use a `Pipeline`.
- Choosing `k` from the scree plot elbow alone without checking downstream performance.
- Reading distances between t-SNE clusters, or cluster size, as meaningful.
- Running t-SNE once with default perplexity and drawing conclusions.
- Using t-SNE output as features for a model.
- Applying PCA to one-hot encoded high-cardinality data and expecting clean results.
- Assuming the highest-variance component is the most predictive.
- Not centring when implementing PCA by hand (scikit-learn does it for you).

## Quick revision cheat sheet

- PCA: centre, find orthogonal directions of maximum variance, project onto the top `k`.
- Components are eigenvectors of the covariance matrix; eigenvalues are variances. Via SVD: `X = U S V^T`, variance `= s^2 / (n - 1)`.
- Explained variance ratio `= lambda_k / sum(lambda)`; keep 90% to 95% cumulative, or use the scree elbow.
- Always standardise features with different units. Fit on train only, use a `Pipeline`.
- `IncrementalPCA` for big data, `KernelPCA` for non-linear, `TruncatedSVD` for sparse.
- t-SNE: local structure, 2D or 3D plots only, perplexity matters, seed matters, do not read cluster distances or sizes.
- UMAP: faster, `n_neighbors` (local versus global) and `min_dist` (tightness), supports `transform`.
- PCA for preprocessing; t-SNE and UMAP for visualisation.
- Library defaults and APIs (scikit-learn, umap-learn) are version-sensitive.

## Sources

- scikit-learn, decomposition (PCA, IncrementalPCA, KernelPCA): https://scikit-learn.org/stable/modules/decomposition.html#pca
- scikit-learn, manifold learning (t-SNE): https://scikit-learn.org/stable/modules/manifold.html#t-distributed-stochastic-neighbor-embedding-t-sne
- UMAP, parameters: https://umap-learn.readthedocs.io/en/latest/parameters.html
- Background (cited from knowledge, not fetched): Hastie, Tibshirani and Friedman, "The Elements of Statistical Learning", ch. 14; van der Maaten and Hinton (2008), "Visualizing data using t-SNE"; McInnes et al. (2018), "UMAP"; Wattenberg et al. (2016), "How to use t-SNE effectively", https://distill.pub/2016/misread-tsne/
