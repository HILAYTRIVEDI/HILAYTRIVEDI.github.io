# Backpropagation and Optimisers

> External reference: researched from public sources, not from the course.

## 1. Neurons and activations

### 1.1 The neuron

**One-line idea:** a neuron computes a weighted sum of its inputs plus a bias, then applies a non-linear activation.

$$z = w^\top x + b, \qquad a = \phi(z)$$

Intuition: without the non-linearity, stacked layers collapse into one linear map. The activation is what lets depth add expressive power.

### 1.2 Common activations

| Activation | Formula | Range | Use | Watch out for |
|---|---|---|---|---|
| Sigmoid | $1/(1+e^{-z})$ | (0, 1) | Binary output probability, gates | Saturates, vanishing gradient, not zero-centred |
| Tanh | $\tanh z$ | (-1, 1) | Recurrent cells | Saturates |
| ReLU | $\max(0, z)$ | [0, inf) | Default for hidden layers | Dead units if always negative |
| Leaky ReLU | $\max(\alpha z, z)$ | (-inf, inf) | Fix for dead ReLUs | Extra hyperparameter |
| GELU, SiLU | smooth ReLU-like | about [-0.17, inf) | Transformers, modern CNNs | Slightly costlier |
| Softmax | $e^{z_i}/\sum_j e^{z_j}$ | (0, 1), sums to 1 | Multi-class output | Use with cross-entropy, ideally from logits |

CS231n recommends ReLU as the practical default for hidden layers.

## 2. Loss functions

### 2.1 Choosing a loss

**One-line idea:** the loss is a single number measuring how wrong the predictions are, and training minimises it.

| Task | Output layer | Loss |
|---|---|---|
| Regression | Linear | MSE (smooth, sensitive to outliers) or MAE / Huber (robust) |
| Binary classification | Sigmoid | Binary cross-entropy |
| Multi-class (one label) | Softmax | Categorical cross-entropy |
| Multi-label | Sigmoid per class | Binary cross-entropy per class |

Cross-entropy for one example with true class $c$: $L = -\log p_c$. It punishes confident wrong predictions heavily. At initialisation with $K$ balanced classes the loss should be about $\ln K$ (about 2.302 for 10 classes), a useful sanity check from CS231n.

Prefer loss functions that take raw logits (for example PyTorch `CrossEntropyLoss`, Keras `from_logits=True`) for numerical stability.

## 3. Backpropagation

### 3.1 The idea

**One-line idea:** backpropagation applies the chain rule layer by layer, from the loss backwards, to get the gradient of the loss with respect to every parameter in one pass.

Intuition: the forward pass stores intermediate values. The backward pass multiplies local derivatives along each path. Reusing shared sub-results is what makes it cheap: the cost is about the same as a forward pass.

Chain rule for a layer: if $L$ depends on $a$, and $a = \phi(z)$, $z = wx + b$:

$$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial a}\cdot\frac{\partial a}{\partial z}\cdot\frac{\partial z}{\partial w}$$

### 3.2 Worked example: one sigmoid neuron with squared error

Setup: $x = 2$, target $y = 1$, weight $w = 0.5$, bias $b = 0.1$, loss $L = \tfrac12 (a - y)^2$, learning rate $\eta = 0.5$.

Forward pass:
1. $z = wx + b = 0.5 \times 2 + 0.1 = 1.1$
2. $a = \sigma(1.1) = 0.7503$
3. $L = \tfrac12 (0.7503 - 1)^2 = 0.0312$

Backward pass:
1. $\partial L / \partial a = a - y = -0.2497$
2. $\partial a / \partial z = a(1 - a) = 0.7503 \times 0.2497 = 0.1873$
3. $\partial L / \partial z = -0.2497 \times 0.1873 = -0.0468$
4. $\partial L / \partial w = \partial L / \partial z \cdot x = -0.0468 \times 2 = -0.0936$
5. $\partial L / \partial b = \partial L / \partial z \cdot 1 = -0.0468$

Update:
- $w \leftarrow 0.5 - 0.5 \times (-0.0936) = 0.5468$
- $b \leftarrow 0.1 - 0.5 \times (-0.0468) = 0.1234$

Check: the new $z = 0.5468 \times 2 + 0.1234 = 1.217$, so $a = 0.771$, closer to the target 1. The loss fell.

### 3.3 Extending to many layers

For layer $l$, define the error signal $\delta^{(l)} = \partial L / \partial z^{(l)}$. Then:

$$\delta^{(l)} = \big( (W^{(l+1)})^\top \delta^{(l+1)} \big) \odot \phi'(z^{(l)}), \qquad \frac{\partial L}{\partial W^{(l)}} = \delta^{(l)} (a^{(l-1)})^\top$$

Notice the repeated factor $\phi'(z)$. For sigmoid, $\phi' \le 0.25$, so deep stacks shrink the gradient (vanishing gradients). This is why ReLU, good initialisation and normalisation matter.

In practice you never code this by hand: autograd frameworks build the graph and run the backward pass. A numerical gradient check is still the best way to test custom layers.

## 4. Gradient descent and its variants

### 4.1 Batch, stochastic and mini-batch

**One-line idea:** step each parameter against its gradient: $\theta \leftarrow \theta - \eta \nabla_\theta L$.

| Variant | Data per step | Behaviour |
|---|---|---|
| Batch GD | Whole dataset | Smooth but slow, memory heavy |
| SGD | One example | Very noisy, cheap steps |
| Mini-batch SGD | 32 to 512 examples | Standard compromise; uses GPU well |

Noise from small batches can help escape sharp minima, but very noisy loss curves suggest the batch is too small (CS231n).

### 4.2 Momentum

**One-line idea:** keep a running velocity so consistent directions speed up and oscillations cancel.

$$v \leftarrow \mu v - \eta g, \qquad \theta \leftarrow \theta + v$$

Typical $\mu = 0.9$. Nesterov momentum evaluates the gradient at the look-ahead point and often works slightly better.

### 4.3 RMSProp

**One-line idea:** divide each step by a running average of recent squared gradients, giving each parameter its own scale.

$$s \leftarrow \rho s + (1-\rho) g^2, \qquad \theta \leftarrow \theta - \frac{\eta}{\sqrt{s} + \epsilon} g$$

Typical $\rho = 0.9$ to $0.99$. Unlike Adagrad (which accumulates all past squares and so keeps shrinking the step), RMSProp forgets old gradients.

### 4.4 Adam

**One-line idea:** momentum plus RMSProp scaling, with bias correction for the early steps.

$$
\begin{aligned}
m_t &= \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \\
\hat m_t &= \frac{m_t}{1-\beta_1^t}, \quad \hat v_t = \frac{v_t}{1-\beta_2^t} \\
\theta_t &= \theta_{t-1} - \eta \frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}
\end{aligned}
$$

Defaults: $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-3}$. Bias correction is needed because $m_0 = v_0 = 0$ biases early estimates towards zero (d2l.ai). CS231n calls Adam the recommended default, with SGD plus Nesterov momentum as an alternative worth trying.

### 4.5 AdamW

**One-line idea:** Adam with weight decay applied directly to the weights instead of being added to the gradient.

Intuition: with plain L2 regularisation inside Adam, the penalty gets divided by $\sqrt{\hat v}$, so decay strength varies per parameter. AdamW decouples it: first shrink $\theta \leftarrow \theta (1 - \eta\lambda)$, then do the Adam step. The PyTorch docs state that weight decay does not accumulate in the momentum or variance. PyTorch defaults: `lr=1e-3`, `betas=(0.9, 0.999)`, `eps=1e-8`, `weight_decay=1e-2`. Reference: "Decoupled Weight Decay Regularization" (Loshchilov and Hutter).

Do not apply weight decay to biases and normalisation parameters; many recipes exclude them.

### 4.6 When to use which optimiser

| Optimiser | Use when | Typical settings | Caveats |
|---|---|---|---|
| SGD | Simple convex-ish problems, baselines | lr 0.01 to 0.1 | Needs lr tuning and schedule |
| SGD + momentum / Nesterov | CNNs for image classification, best final accuracy with tuning | lr 0.1, $\mu$ 0.9, with decay | Slower to tune |
| RMSProp | Recurrent nets, some RL | lr 1e-3 to 1e-4 | Largely superseded by Adam |
| Adam | Default start for almost anything, noisy or sparse gradients | lr 1e-3 (1e-4 for fine-tuning) | Weaker regularisation; can generalise slightly worse than tuned SGD |
| AdamW | Transformers, fine-tuning, any model that needs weight decay | lr 1e-4 to 5e-5 for fine-tuning, decay 0.01 to 0.1 | Tune decay separately |
| Adagrad | Very sparse features | lr 0.01 | Step size decays to nothing |

Rule of thumb: start with AdamW and a schedule; switch to SGD with momentum if you are chasing the last bit of accuracy on a CNN and have time to tune.

## 5. Learning-rate schedules

### 5.1 Why schedule

**One-line idea:** use a larger learning rate early to move fast, then reduce it to settle into a minimum.

CS231n warns that decaying too slowly wastes compute, while decaying too fast cools the model before it reaches a good minimum.

| Schedule | Rule | Use |
|---|---|---|
| Step decay | Multiply by a factor (for example 0.1) every N epochs | Classic CNN training |
| Exponential | $\eta_0 e^{-kt}$ | Smooth decay |
| Reduce on plateau | Cut lr when validation metric stalls | Little tuning, safe default |
| Cosine annealing | Follow a half cosine from $\eta_0$ to near 0 | Common modern default |
| Linear warmup then decay | Ramp up over first steps, then decay | Transformers, large batches, Adam |
| One-cycle | Warm up to a peak then anneal | Fast training with SGD or Adam |
| Warm restarts | Cosine with periodic resets | Ensembles, exploration |

Warmup matters with Adam because the second-moment estimate is unreliable in the first steps.

PyTorch (version-sensitive; check current docs): call `optimizer.step()` per batch, and `scheduler.step()` after it (per epoch for most schedulers, per batch for `OneCycleLR`). Calling them in the wrong order skips the first learning-rate value. Schedulers include `StepLR`, `CosineAnnealingLR`, `OneCycleLR`, `LinearLR`, `ReduceLROnPlateau` and `SequentialLR`.

```python
import torch

opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=num_epochs)

for epoch in range(num_epochs):
    for xb, yb in loader:
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    sched.step()
```

## 6. Batch normalisation

### 6.1 The idea

**One-line idea:** normalise each layer's inputs over the mini-batch to zero mean and unit variance, then rescale with learnable parameters.

$$\hat x = \frac{x - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \qquad y = \gamma \hat x + \beta$$

Intuition: it keeps activations in a well-behaved range, so higher learning rates are possible and the network is far less sensitive to initialisation (CS231n). It is typically placed after a dense or convolutional layer and before the activation, though after-activation placement also works.

Key points:
- Training uses batch statistics; inference uses running averages. Forgetting `model.eval()` (PyTorch) is a classic bug.
- It works poorly with very small batches. Alternatives: LayerNorm (Transformers, RNNs), GroupNorm (small-batch vision).
- It adds mild regularisation through batch noise.

| Normalisation | Normalises over | Typical home |
|---|---|---|
| BatchNorm | Batch (per feature or channel) | CNNs, MLPs |
| LayerNorm | Features of one example | Transformers, RNNs |
| GroupNorm | Channel groups of one example | Small-batch vision |

## 7. Weight initialisation

### 7.1 The idea

**One-line idea:** choose initial weights so signal and gradient variance stay roughly constant from layer to layer.

- All-zero weights make every neuron identical and give identical gradients, so symmetry is never broken (CS231n).
- Weights that are too small shrink signals and gradients; too large saturate or explode them.

| Scheme | Variance of weights | Use with |
|---|---|---|
| Xavier / Glorot | $2/(n_{in} + n_{out})$ | Tanh, sigmoid, linear (Keras default for dense) |
| He / Kaiming | $2/n_{in}$ | ReLU and variants |
| Orthogonal | n/a | Recurrent weights (Keras LSTM default) |
| LeCun | $1/n_{in}$ | SELU |

Biases are usually zero. With batch normalisation, initialisation matters much less.

## 8. Common training failures and fixes

### 8.1 Diagnostic table

| Symptom | Likely cause | Fixes |
|---|---|---|
| Loss is `NaN` or `inf` | Learning rate too high, exploding gradients, log of zero, bad data | Lower lr, clip gradients, check inputs for NaN, use logits-based loss |
| Loss does not decrease | lr too low or too high, bug, wrong labels, dead ReLUs | Overfit a tiny batch first, tune lr, check data pipeline and loss |
| Loss stuck at about $\ln K$ | Model predicting priors, no learning | Check labels, scaling, lr, frozen layers |
| Train loss falls, validation rises | Overfitting | More data or augmentation, dropout, weight decay, early stopping, smaller model |
| Both train and validation poor | Underfitting | Bigger model, train longer, higher lr, better features |
| Noisy loss curve | Batch too small, lr too high | Larger batch, lower lr, smoothing |
| Loss plateaus then drops after lr cut | lr too high late in training | Use a schedule |
| Vanishing gradients (early layers static) | Sigmoid or tanh depth, poor init | ReLU or GELU, He init, BatchNorm or LayerNorm, residual connections |
| Exploding gradients | Deep or recurrent nets, high lr | Gradient clipping, lower lr, normalisation |
| Dead ReLUs | Large negative bias or lr | Leaky ReLU, lower lr, He init |
| Validation metric differs from training at inference | BatchNorm or dropout still in train mode | `model.eval()` (PyTorch), `training=False` (Keras) |

### 8.2 Sanity checks before a long run (from CS231n)

1. With small random weights and no regularisation, check the initial loss equals chance (about $\ln K$).
2. Increase regularisation and confirm the loss goes up.
3. Overfit about 20 examples to near-zero loss. If you cannot, there is a bug.
4. Watch the update-to-weight ratio, aiming for roughly $10^{-3}$. Much lower means lr is too low; much higher means too high.
5. Inspect activation and gradient histograms for saturation or dead units.
6. Plot train and validation curves together; a large gap means overfitting.

## Use cases

- Any supervised deep network: the same backprop plus optimiser loop trains CNNs, RNNs and Transformers.
- Fine-tuning pretrained models: AdamW, low lr (1e-5 to 5e-5), warmup, linear or cosine decay.
- Training CNNs from scratch on images: SGD with momentum, step or cosine schedule, BatchNorm, He init.
- Training RNNs: Adam or RMSProp, gradient clipping, orthogonal recurrent init.
- Debugging unfamiliar models: the sanity checks in 8.2.

## Common mistakes

- Forgetting `zero_grad()` so gradients accumulate across batches.
- Applying softmax in the model and then a loss that applies softmax again.
- Not scaling inputs (features on very different scales slow or destabilise training).
- Tuning many hyperparameters at once; change the learning rate first, it matters most.
- Evaluating with BatchNorm and dropout still in training mode.
- Weight decay applied to biases and norm parameters, or confusing L2-in-Adam with AdamW.
- Calling `scheduler.step()` before `optimizer.step()`, or per batch when it expects per epoch.
- Comparing optimisers at a single untuned learning rate.
- Judging only on training loss.

## Quick revision cheat sheet

- Neuron: $a = \phi(w^\top x + b)$. ReLU for hidden layers, sigmoid or softmax at the output for classification.
- Loss: MSE for regression, cross-entropy for classification; initial loss about $\ln K$.
- Backprop: chain rule from loss to weights; $\delta^{(l)} = (W^\top \delta^{(l+1)}) \odot \phi'(z)$, $\partial L/\partial W = \delta\, a_{prev}^\top$.
- Worked example: $w$ 0.5 to 0.547 and $b$ 0.1 to 0.123 after one step at lr 0.5.
- SGD: $\theta \leftarrow \theta - \eta g$. Momentum adds velocity. RMSProp scales by recent squared gradients.
- Adam = momentum + RMSProp + bias correction; defaults 0.9, 0.999, 1e-8, lr 1e-3.
- AdamW = Adam with decoupled weight decay (default 0.01 in PyTorch).
- Schedules: warmup then cosine or linear decay for Adam; step or cosine for SGD; plateau as a safe default.
- BatchNorm: normalise per batch then scale and shift; use `eval()` at inference; LayerNorm for sequences.
- Init: He for ReLU, Xavier for tanh or sigmoid, never all zeros.
- Debug order: overfit a tiny batch, check initial loss, tune lr, then regularise.
- Exploding gradients: clip. Vanishing: ReLU, good init, normalisation, residual connections.

## Sources

- https://cs231n.github.io/neural-networks-3/
- https://cs231n.github.io/neural-networks-2/
- https://d2l.ai/chapter_optimization/adam.html
- https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html
- https://docs.pytorch.org/docs/2.14/optim.html
- https://keras.io/api/layers/recurrent_layers/lstm/
