#### Patially copy from codes in MASKGIT paper

from typing import Any, Union

import flax.linen as nn
import jax
import jax.numpy as jnp
import sys 
# sys.path.append('PROTOKEN')
from onescience.flax_models.protoken.common.config_load import Config
from onescience.flax_models.protoken.loss.utils import square_euclidean_distance


def squared_euclidean_distance_fn(a: jnp.ndarray,
                               b: jnp.ndarray,
                               a2: Union[jnp.ndarray, jnp.float32] = None,
                               b2: Union[jnp.ndarray, jnp.float32] = None,
                               precision: Any = None) -> jnp.ndarray:
    """Computes the pairwise squared Euclidean distance.

    Args:
        a: float32: (n, d): An array of points.
        b: float32: (m, d): An array of points.
        b2: float32: (d, m): b square transpose.
        precision: use DEFAULT precision by default

    Returns:
        d: float32: (n, m): Where d[i, j] is the squared Euclidean distance between
        a[i] and b[j].
    """
    if a2 is None:
        a2 = jnp.sum(a**2, axis=1, keepdims=True)
    if b2 is None:
        b2 = jnp.sum(b.T**2, axis=0, keepdims=True)
    ab = jnp.matmul(a, b.T, precision=precision)
    d = a2 - 2 * ab + b2
    return d

def entropy_loss_fn(affinity, mask, loss_type="softmax", temperature=1.0):
    """Calculates the entropy loss."""
    affinity = affinity * mask[..., None] + (1.0 - mask[..., None]) * -1e5
    affinity /= temperature
    probs = jax.nn.softmax(affinity, axis=-1) # (Nres, Ncode)
    log_probs = jax.nn.log_softmax(affinity + 1e-5, axis=-1)
    if loss_type == "softmax":
        target_probs = probs
    elif loss_type == "argmax":
        codes = jnp.argmax(affinity, axis=-1)
        onehots = jax.nn.one_hot(
            codes, affinity.shape[-1], dtype=affinity.dtype)
        onehots = probs - jax.lax.stop_gradient(probs - onehots)
        target_probs = onehots
    else:
        raise ValueError("Entropy loss {} not supported".format(loss_type))
    avg_probs = jnp.sum(target_probs * mask[..., None], axis=0) / jnp.sum(mask)
    avg_entropy = -jnp.sum(avg_probs * jnp.log(avg_probs + 1e-5))
    sample_entropy = -jnp.sum(jnp.sum(target_probs * log_probs, axis=-1) * mask) / jnp.sum(mask)
    loss = sample_entropy - avg_entropy
    return loss

class VQTokenizer(nn.Module):
    """Basic vector quantizer."""
    config: Config
    dtype: int = jnp.float32

    @nn.compact
    def __call__(self, x, mask):
        #### shape: x (Nres, d), mask: (Nres)
        
        #### initialize
        train = self.config.train
        codebook_size = self.config.num_code
        codebook = self.param(
            "codebook",
            jax.nn.initializers.variance_scaling(
                scale=1.0, mode="fan_in", distribution="uniform"),
            (codebook_size, x.shape[-1]))
        codebook = jnp.asarray(codebook, dtype=self.dtype)
        l2_norm = self.config.l2_norm
        stochastic_sampling = self.config.stochastic_sampling
        sampling_temperature = self.config.sampling_temperature
        
        #### quantize
        a2, b2 = None, None
        if l2_norm:
            _dtype = x.dtype
            x = x.astype(jnp.float32)
            x = x + jnp.expand_dims(1.0 - mask, axis=-1).astype(jnp.float32) * 1e-6 ##### prevent nan bug
            x = x / jnp.maximum(jnp.linalg.norm(x, axis=-1, keepdims=True), 1e-6) 
            x = x.astype(_dtype)
            a2, b2 = 1.0, 1.0
        distances = squared_euclidean_distance_fn(x, codebook, a2=a2, b2=b2)
        
        logits = -distances
        if stochastic_sampling:
            noise = jax.random.gumbel(
                self.make_rng("gumbel_noise"), logits.shape, dtype=self.dtype)
            logits = logits / sampling_temperature + noise
        encoding_indices = jnp.argmax(logits, axis=-1)
        encodings = jax.nn.one_hot(
            encoding_indices, codebook_size, dtype=self.dtype)
        quantized = self.quantize(encodings)
        
        #### loss
        result_dict = dict()
        if train:
            e_latent_loss = jnp.sum(
                square_euclidean_distance(
                    jax.lax.stop_gradient(quantized), x, normalized=l2_norm) * mask) /\
                        (jnp.sum(mask) + 1e-6)
            q_latent_loss = jnp.sum(
                square_euclidean_distance(
                    quantized, jax.lax.stop_gradient(x), normalized=l2_norm) * mask) /\
                        (jnp.sum(mask) + 1e-6)
            entropy_loss = 0.0
            if self.config.entropy_loss_type != "disabled":
                entropy_loss = entropy_loss_fn(
                    -distances,
                    mask,
                    loss_type=self.config.entropy_loss_type,
                    temperature=self.config.entropy_temperature
                )
            e_latent_loss = jnp.asarray(e_latent_loss, jnp.float32)
            q_latent_loss = jnp.asarray(q_latent_loss, jnp.float32)
            entropy_loss = jnp.asarray(entropy_loss, jnp.float32)
            result_dict = dict(
                # quantizer_loss=loss,
                e_latent_loss=e_latent_loss,
                q_latent_loss=q_latent_loss,
                entropy_loss=entropy_loss)
        quantized = x + jax.lax.stop_gradient(quantized - x)

        result_dict.update({
            "encodings": encodings,
            "encoding_indices": encoding_indices,
            "code_count": jnp.bincount(encoding_indices.flatten(), 
                                       weights=mask.flatten(), length=codebook_size).astype(jnp.float32),
            "raw": x,
        })
        return quantized, result_dict

    def quantize(self, z: jnp.ndarray) -> jnp.ndarray:
        codebook = jnp.asarray(
            self.variables["params"]["codebook"], dtype=self.dtype)
        return jnp.dot(z, codebook)

    def get_codebook(self) -> jnp.ndarray:
        return jnp.asarray(self.variables["params"]["codebook"], dtype=self.dtype)

    def decode_ids(self, ids: jnp.ndarray) -> jnp.ndarray:
        codebook = self.variables["params"]["codebook"]
        return jnp.take(codebook, ids, axis=0)
    
#################################################
## The GumbelVQTokenizer code is not modified yet
#################################################
class GumbelVQTokenizer(nn.Module):
    """Gumbel VQ."""
    config: Config
    dtype: int = jnp.float32

    @nn.compact
    def __call__(self, x, mask, tau=1.0):
        train = self.config.train
        codebook_size = self.config.num_code
        codebook = self.param(
            "codebook",
            jax.nn.initializers.variance_scaling(
                scale=1.0, mode="fan_in", distribution="uniform"),
            (codebook_size, x.shape[-1]))
        codebook = jnp.asarray(codebook, dtype=self.dtype)
        l2_norm = self.config.l2_norm
        
        #### quantize
        a2, b2 = None, None
        if l2_norm:
            _dtype = x.dtype
            x = x.astype(jnp.float32)
            x = x + jnp.expand_dims(1.0 - mask, axis=-1).astype(jnp.float32) * 1e-6 ##### prevent nan bug
            x = x / jnp.maximum(jnp.linalg.norm(x, axis=-1, keepdims=True), 1e-6) 
            x = x.astype(_dtype)
            a2, b2 = 1.0, 1.0
        distances = squared_euclidean_distance_fn(x, codebook, a2=a2, b2=b2)
        
        result_dict = dict()
        encoding_indices = jnp.argmin(distances, axis=-1)
        if train:
            noise = jax.random.gumbel(
                self.make_rng("gumbel_noise"), distances.shape, dtype=self.dtype)
            encodings = jax.nn.softmax((-distances + noise) / tau, axis=-1)
            quantized = self.quantize(encodings)
        else:
            encodings = jax.nn.one_hot(
                encoding_indices, codebook_size, dtype=self.dtype)
            quantized = self.quantize(encodings)
        result_dict.update({
            # "quantizer_loss": 0.0,
            "encodings": encodings,
            "encoding_indices": encoding_indices,
        })
        return quantized, result_dict

    def quantize(self, z: jnp.ndarray) -> jnp.ndarray:
        codebook = jnp.asarray(
            self.variables["params"]["codebook"], dtype=self.dtype)
        return jnp.dot(z, codebook)

    def decode_ids(self, ids: jnp.ndarray) -> jnp.ndarray:
        return jnp.take(self.variables["params"]["codebook"], ids, axis=0)