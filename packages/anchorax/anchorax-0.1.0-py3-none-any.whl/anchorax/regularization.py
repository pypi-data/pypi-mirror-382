import jax
import jax.numpy as jnp
import jax.random as jr
from einops import rearrange
from jaxtyping import PRNGKeyArray


def lipschitz_normalization_factor(
    f,
    u: jax.Array,
    v: jax.Array,
    *,
    gamma: float,
    num_layers: int = 1,
    key: PRNGKeyArray,
):
    """One-step stochastic check for gamma-Lipschitzness of u -> f(u, v)."""
    key_u, key_v = jr.split(key)
    noise_u = jr.normal(key_u, u.shape, dtype=u.dtype)
    noise_v = jr.normal(key_v, v.shape, dtype=v.dtype)

    w = u + noise_u
    v_noisy = v + noise_v

    Rwv = f(w, v_noisy)
    Ruv = f(u, v_noisy)

    R_diff_norm = jnp.mean(
        jnp.linalg.norm(rearrange(Rwv - Ruv, "b c h w -> b (c h w)"), axis=1)
    )
    u_diff_norm = jnp.mean(
        jnp.linalg.norm(rearrange(w - u, "b c h w -> b (c h w)"), axis=1)
    )

    R_is_gamma_lip = R_diff_norm <= gamma * u_diff_norm

    def calculate_factor():
        violation_ratio = gamma * u_diff_norm / (R_diff_norm + 1e-6)
        return violation_ratio ** (1.0 / num_layers)

    def identity_factor():
        return jnp.array(1.0, dtype=u.dtype)

    return jax.lax.cond(R_is_gamma_lip, identity_factor, calculate_factor)


def jac_reg(f, x: jax.Array, u0: jax.Array, *, vecs: int = 2, key: PRNGKeyArray):
    """Hutchinson estimator for ||J||_F^2 where J = ∂ f(u0, x) / ∂ u0."""

    def _f(z):
        return f(z, x)

    f0, vjp_fun = jax.vjp(_f, u0)
    size = u0.size

    def single_sample(k):
        v = jr.normal(k, f0.shape, dtype=f0.dtype)
        (jt_v,) = vjp_fun(v)  # Jᵀ · v
        return jnp.sum(jt_v**2)

    keys = jr.split(key, vecs)
    estimates = jax.vmap(single_sample)(keys)
    return jnp.mean(estimates) / size
