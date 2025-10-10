import jax
import jax.numpy as jnp
from flax import linen as nn
from flax import nnx
from gemma.gm.utils import _dtype_params


class GemmaRMSNorm(nnx.Module):
    """
    Gemma RMSNorm layer.

    This layer (Linen version) is used in the original Gemma implementation [1]
    and behaves slightly differently than nnx.RMSNorm. We use it here
    for compatibility with Gemma's weights.
    """

    def __init__(
        self,
        num_features: int,
        *,
        param_dtype: jax.typing.DTypeLike = jnp.bfloat16,
        rngs: nnx.Rngs | None = None,  # not used
    ):
        self.scale = nnx.Param(jnp.zeros(shape=num_features, dtype=param_dtype))

    def __call__(self, x):
        scale = self.scale
        var = jnp.mean(jnp.square(x), axis=-1, keepdims=True)

        # Jax.lax.rsqrt is used because it returns different floats than
        # jnp.reciprocal(jnp.sqrt(var + 1e-06))
        normed_inputs = x * jax.lax.rsqrt(var + 1e-06)

        # normed_inputs is a rank-K tensor, K > 1 (K is typically 2 or 3). scale is
        # a rank-1 tensor. To avoid implicit rank-promotion, reshape scale to
        # a (1, ..., 1, D) tensor, so the rank of scale matches normed_inputs.
        scale = jnp.expand_dims(scale, axis=range(len(x.shape) - 1))
        normed_inputs = normed_inputs * (1 + scale)
        return normed_inputs



class RMSNorm(nn.Module):
  """RMSNorm layer."""

  @nn.compact
  def __call__(self, x):
      scale = self.param('scale', nn.initializers.zeros_init(), (x.shape[-1]))
      var = jnp.mean(jnp.square(x), axis=-1, keepdims=True)

      # Jax.lax.rsqrt is used because it returns different floats than
      # jnp.reciprocal(jnp.sqrt(var + 1e-06))
      normed_inputs = x * jax.lax.rsqrt(var + 1e-06)

      # normed_inputs is a rank-K tensor, K > 1 (K is typically 2 or 3). scale is
      # a rank-1 tensor. To avoid implicit rank-promotion, reshape scale to
      # a (1, ..., 1, D) tensor, so the rank of scale matches normed_inputs.
      scale = jnp.expand_dims(scale, axis=range(len(x.shape) - 1))
      normed_inputs = normed_inputs * (1 + scale)
      return normed_inputs


def main():
    batch_size = 2
    num_featues = 32
    dtype = jnp.bfloat16
    seed = 104
    key_x, key_norm = jax.random.split(jax.random.key(seed))
    x = jax.random.normal(key_x, (batch_size, num_featues), dtype=jnp.bfloat16)

    with _dtype_params.initialize_param_with_dtype(dtype):
        norm_nn = RMSNorm()
        # norm.init() would set 'scale' to all zeros; we initialize it to random instead
        variables = {"params": {"scale": jax.random.normal(key_norm, (num_featues,), dtype=dtype)}}

        out_nn = norm_nn.apply(variables, x)
        out_nn_jit = jax.jit(norm_nn.apply)(variables, x)

    norm_nnx = GemmaRMSNorm(num_features=num_featues)
    norm_nnx.scale.value = variables["params"]["scale"]
    out_nnx = norm_nnx(x)
    out_nnx_jit = nnx.jit(norm_nnx)(x)
    out_nnx_jj = jax.jit(norm_nnx)(x)

    jnp.all(out_nn == out_nnx)
    jnp.all(out_nn == out_nn_jit)
    jnp.all(out_nnx == out_nnx_jit)
    jnp.all(out_nnx == out_nnx_jj)
    jnp.all(out_nn_jit == out_nnx_jit)

