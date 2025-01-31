import jax

class Transformer:
  weights: jax.numpy.ndarray
  num_layers: int
  num_heads: int
  hidden_dim: int
  ffwd_hidden_factor: int
  vocab: list[str]
  __weight_index: int

  def __init__(self, num_layers, num_heads, hidden_dim, ffwd_hidden_factor, vocab):
    pass

  def __call__(self, state: jax.numpy.ndarray) -> jax.numpy.ndarray:
    self.__weight_index = 0
    state = self.hidden_from_vocab(state)
    for _ in range(self.num_layers):
      state = state + self.__attn(self.__norm(state))
      state = state + self.__ffwd(self.__norm(state))
    state = self.vocab_from_hidden(state)
    return state

  def update(self, dataset):
    pass

  def vocab_from_string(self, string: str) -> jax.numpy.ndarray:
    pass

  def string_from_vocab(self, tokens: jax.numpy.ndarray) -> str:
    pass

  def hidden_from_vocab(self, state):
    pass

  def vocab_from_hidden(self, state):
    pass

  def __get_weights(self, shape):
    # Get the next set of weights, from the current weight index.
    pass

  def __attn(self, state):
    # Multi-head self-attention.
    pass

  def __ffwd(self, state):
    # Feedforward with ReLU activation.
    pass

  def __norm(self, state):
    # Layer normalization.
    pass
