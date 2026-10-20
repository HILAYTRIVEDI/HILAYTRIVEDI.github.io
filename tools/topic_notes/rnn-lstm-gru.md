# RNN, LSTM and GRU

> External reference: researched from public sources, not from the course.

## 1. Recurrent neural networks

### 1.1 What an RNN is

**One-line idea:** an RNN reads a sequence one step at a time and carries a hidden state that summarises everything seen so far.

Intuition: a feed-forward network treats each input independently. An RNN reuses the same weights at every time step and passes a memory vector forward, so the output at step t can depend on earlier inputs.

$$h_t = \tanh(W_{xh} x_t + W_{hh} h_{t-1} + b_h), \qquad y_t = W_{hy} h_t + b_y$$

Key points:
- The weights are shared across time, so the model handles any sequence length.
- Unrolled in time, an RNN is a very deep network (one layer per step) with tied weights.

### 1.2 Input and output patterns

| Pattern | Example | Keras setting |
|---|---|---|
| Many to one | Sentiment of a review, classify a sensor window | `return_sequences=False` |
| Many to many (aligned) | Per-token tagging, frame-level speech labels | `return_sequences=True` |
| One to many | Image captioning (decoder side) | Feed the previous output back in |
| Many to many (encoder-decoder) | Translation (older RNN approach) | Encoder state initialises decoder |

### 1.3 Training: backpropagation through time

**One-line idea:** BPTT is ordinary backpropagation applied to the unrolled network, summing gradients for the shared weights over all steps.

Intuition: the gradient for $W_{hh}$ collects a contribution from every time step. Each contribution passes through a long chain of Jacobians. Full BPTT over long sequences is slow and unstable, so practitioners use **truncated BPTT**: backpropagate only $\tau$ steps, then detach the hidden state and continue (d2l.ai describes this as approximating the true gradient while favouring short-term influence).

## 2. Vanishing and exploding gradients

### 2.1 Why it happens

**One-line idea:** the gradient through many steps is a product of many similar matrices, so it shrinks or grows exponentially.

Intuition: the gradient flowing from step T back to step k contains a product of terms like $W_{hh}^\top \, \mathrm{diag}(\tanh'(\cdot))$. d2l.ai puts it as powers of $W_{hh}^\top$: eigenvalues smaller than 1 vanish and eigenvalues larger than 1 diverge. The $\tanh'$ factor is at most 1, which pushes towards vanishing.

| Problem | Symptom | Consequence |
|---|---|---|
| Vanishing | Early steps get almost no gradient; loss plateaus | Cannot learn long-range dependencies |
| Exploding | Loss spikes, `NaN`, huge weight updates | Training diverges |

### 2.2 Fixes

| Problem | Fix | Note |
|---|---|---|
| Exploding | **Gradient clipping** (by norm) | Rescale the gradient if its norm exceeds a threshold, for example 1.0 to 5.0 |
| Exploding | Lower learning rate | Often combined with clipping |
| Vanishing | **Gated cells** (LSTM, GRU) | Additive state update gives a gradient path |
| Vanishing | Orthogonal recurrent initialisation | Keras LSTM default for recurrent weights |
| Vanishing | Skip or residual connections, attention | Shorten the path between distant steps |
| Both | Truncated BPTT | Limits chain length |

Clipping by norm: $g \leftarrow g \cdot \min(1, c / \lVert g \rVert)$. It keeps the direction and only caps the step size. It does not cure vanishing gradients.

## 3. LSTM

### 3.1 The core idea

**One-line idea:** an LSTM keeps a separate cell state that is updated by addition, with gates deciding what to forget, write and reveal.

Intuition (Colah's post): the cell state $C_t$ runs along the sequence like a conveyor belt with only small linear interactions. Because $C_t = f_t \odot C_{t-1} + \dots$, the gradient along the cell state is multiplied by the forget gate rather than by a weight matrix and a squashing function at every step. If $f_t$ is near 1, information and gradient flow almost unchanged.

### 3.2 The gates

| Gate | Activation | Role |
|---|---|---|
| Forget $f_t$ | sigmoid | Which parts of the old cell state to keep (1) or discard (0) |
| Input $i_t$ | sigmoid | Which parts of the candidate to write |
| Candidate $\tilde C_t$ | tanh | Proposed new content, range -1 to 1 |
| Output $o_t$ | sigmoid | Which parts of the cell state to expose as $h_t$ |

$$
\begin{aligned}
f_t &= \sigma(W_f [h_{t-1}, x_t] + b_f) \\
i_t &= \sigma(W_i [h_{t-1}, x_t] + b_i) \\
\tilde C_t &= \tanh(W_c [h_{t-1}, x_t] + b_c) \\
C_t &= f_t \odot C_{t-1} + i_t \odot \tilde C_t \\
o_t &= \sigma(W_o [h_{t-1}, x_t] + b_o) \\
h_t &= o_t \odot \tanh(C_t)
\end{aligned}
$$

Practical notes:
- Only $h_t$ goes to the next layer; $C_t$ is internal (d2l.ai).
- Keras `unit_forget_bias=True` (default) adds 1 to the forget-gate bias at initialisation, so the cell starts by remembering. The Keras docs recommend this, citing Jozefowicz et al.
- Parameter count per layer: $4 \times (d_{in} h + h^2 + h)$, four times a plain RNN of the same size.

## 4. GRU

### 4.1 The core idea

**One-line idea:** a GRU merges the cell and hidden state and uses two gates, so it is a lighter LSTM.

Intuition: the **update gate** $z_t$ decides how much of the old state to keep versus replace, playing the role of forget and input gates together. The **reset gate** $r_t$ decides how much of the old state feeds the candidate.

$$
\begin{aligned}
r_t &= \sigma(W_r [h_{t-1}, x_t]) \\
z_t &= \sigma(W_z [h_{t-1}, x_t]) \\
\tilde h_t &= \tanh(W [r_t \odot h_{t-1}, x_t]) \\
h_t &= z_t \odot h_{t-1} + (1 - z_t) \odot \tilde h_t
\end{aligned}
$$

This follows the d2l.ai convention, where $z_t$ close to 1 keeps the old state. Some libraries swap the roles of $z_t$ and $1 - z_t$, so do not compare equations across sources without checking.

### 4.2 LSTM versus GRU

| Aspect | LSTM | GRU |
|---|---|---|
| Gates | 3 (forget, input, output) | 2 (update, reset) |
| State | Cell $C_t$ and hidden $h_t$ | Hidden $h_t$ only |
| Parameters | About 4 blocks per layer | About 3 blocks per layer |
| Speed | Slower | Faster, less memory |
| Typical accuracy | Similar; no consistent winner | Similar; often better on small data |
| Default choice | Longer sequences, more capacity | Quick baseline, limited data or compute |

Treat the choice as a hyperparameter: try GRU first for speed, LSTM if it underfits.

## 5. Bidirectional RNNs

### 5.1 How they work

**One-line idea:** run one RNN left to right and another right to left, then concatenate their states at each step.

Intuition: the meaning of a word often depends on words after it. A bidirectional layer gives every position both past and future context. It has two sets of parameters and roughly doubles the cost (d2l.ai).

### 5.2 When not to use one

Do not use a bidirectional model where the future is unavailable at prediction time: forecasting, next-token language modelling, real-time streaming. It would leak future inputs in training that do not exist at inference.

| Task | Bidirectional? |
|---|---|
| Sentiment, named-entity recognition, tagging | Yes (whole sequence available) |
| Offline speech recognition | Yes |
| Time-series forecasting | No |
| Language modelling, text generation | No |
| Live streaming prediction | No (or only with a small look-ahead) |

## 6. RNNs versus Transformers

### 6.1 The trade-off

**One-line idea:** Transformers replace recurrence with attention, which parallelises training and reaches any position in one step, at the cost of quadratic memory in sequence length.

| Aspect | RNN, LSTM, GRU | Transformer |
|---|---|---|
| Training parallelism | Sequential over time steps | Fully parallel over positions |
| Long-range dependencies | Weak to moderate, even with gates | Strong (direct attention) |
| Cost per sequence | Linear in length | Quadratic in length (full attention) |
| Inference memory | Constant state size | Grows with context (KV cache) |
| Data needed | Works with small data | Usually needs more data or pretraining |
| Pretrained models | Few | Abundant (BERT, GPT families, speech and time-series models) |

### 6.2 When to use which

| Situation | Suggested choice |
|---|---|
| Most modern NLP tasks | Transformer (fine-tune a pretrained model) |
| Small tabular-like time series, few thousand samples | GRU or LSTM, or gradient boosting with lag features |
| Streaming, on-device, tight memory | GRU or LSTM |
| Very long sequences with limited budget | RNN, state-space models, or efficient attention variants |
| Teaching or understanding sequence modelling | Start with RNN, then attention |

Always compare against a simple baseline (naive forecast, moving average, logistic regression on TF-IDF) before building a recurrent model.

## 7. Use cases

### 7.1 Time series

- Forecasting demand, energy load, sensor readings, finance (with caution about noise and non-stationarity).
- Anomaly detection by predicting the next window and flagging large errors.
- Pattern: slide a window of length L over the series, predict the next value(s). Scale inputs, split by time (never randomly), and use a unidirectional layer.

### 7.2 Text

- Sentiment classification, sequence tagging (NER, part of speech), and older machine translation and captioning decoders.
- Pattern: tokenise, embed (`Embedding` layer or pretrained vectors), then a (bidirectional) LSTM or GRU, then a dense head.

### 7.3 Speech and audio

- Acoustic modelling, keyword spotting, speaker or emotion classification.
- Pattern: convert audio to log-mel spectrogram frames, feed frames as the sequence. Often combined with convolutions in front and CTC loss for transcription. Modern large systems are Transformer-based, but small streaming models still use GRU or LSTM.

## 8. Keras code sketch

Keras APIs change between releases (Keras 2 with `tf.keras`, Keras 3 multi-backend). Treat this as **version-sensitive** and check the current docs.

```python
import keras
from keras import layers

# Text classification: bidirectional LSTM
model = keras.Sequential([
    layers.Input(shape=(None,), dtype="int32"),            # token ids
    layers.Embedding(input_dim=20000, output_dim=128, mask_zero=True),
    layers.Bidirectional(layers.LSTM(64, return_sequences=True)),
    layers.Bidirectional(layers.LSTM(32)),                 # last output only
    layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(
    optimizer=keras.optimizers.Adam(1e-3, clipnorm=1.0),   # gradient clipping
    loss="binary_crossentropy",
    metrics=["accuracy"],
)
model.fit(x_train, y_train, validation_split=0.2, epochs=5, batch_size=64)
```

```python
# Time-series forecasting: GRU over windows, unidirectional
model = keras.Sequential([
    layers.Input(shape=(window, n_features)),
    layers.GRU(64),
    layers.Dense(1),
])
model.compile(optimizer="adam", loss="mse")
```

Useful arguments from the Keras LSTM docs:
- `return_sequences`: return every step (needed before stacking another recurrent layer or for per-step outputs).
- `return_state`: also return the final states (used for encoder-decoder).
- `dropout` and `recurrent_dropout`: input and recurrent dropout.
- `stateful`: carry state across batches.
- cuDNN fast path on GPU requires `activation="tanh"`, `recurrent_activation="sigmoid"`, `recurrent_dropout=0`, `unroll=False`, `use_bias=True`, and right-padded masks. Using `recurrent_dropout > 0` silently drops you to the much slower kernel.

## Common mistakes

- Using a bidirectional layer for forecasting or generation (future leakage).
- Random train/test split on time series instead of splitting by time.
- Forgetting to scale inputs or to clip gradients, then seeing `NaN` loss.
- Forgetting `return_sequences=True` on all but the last stacked recurrent layer (shape error).
- Padding without masking, so the model learns from padding tokens.
- Very long sequences with a plain RNN and no gates.
- Skipping a naive baseline and over-crediting the model.
- Using `recurrent_dropout` on GPU without noticing the speed drop.
- Reading "LSTM beats GRU" as a rule; results depend on data.

## Quick revision cheat sheet

- RNN: shared weights, hidden state $h_t = \tanh(W_{xh}x_t + W_{hh}h_{t-1} + b)$.
- BPTT: backprop on the unrolled graph; truncate for long sequences.
- Vanishing or exploding gradient: repeated products of $W_{hh}$; eigenvalues below 1 vanish, above 1 explode.
- Exploding: clip by norm. Vanishing: gates, orthogonal init, attention.
- LSTM: forget, input, output gates; $C_t = f \odot C_{t-1} + i \odot \tilde C$; $h_t = o \odot \tanh(C_t)$.
- GRU: update and reset gates; no separate cell state; fewer parameters.
- Bidirectional: forward and backward RNN concatenated; only when the whole sequence is known.
- Transformers: parallel, strong long-range, quadratic cost; the default for NLP today.
- RNNs still fit small data, streaming and low-memory settings.
- Keras: `Embedding`, `LSTM` or `GRU`, `Bidirectional`, `return_sequences`, `clipnorm`.

## Sources

- https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- https://d2l.ai/chapter_recurrent-modern/lstm.html
- https://d2l.ai/chapter_recurrent-modern/gru.html
- https://d2l.ai/chapter_recurrent-modern/bi-rnn.html
- https://d2l.ai/chapter_recurrent-neural-networks/bptt.html
- https://keras.io/api/layers/recurrent_layers/lstm/
