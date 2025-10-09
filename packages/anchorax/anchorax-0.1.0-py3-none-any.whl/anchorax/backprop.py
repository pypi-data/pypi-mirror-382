from typing import Callable

import equinox as eqx
import jax
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from anchorax.solvers import broyden, masked_rmatvec, picard


@eqx.filter_custom_vjp
def jfb(
    diff_args,
    static,
    *,
    solver: Callable = picard,
    inference: bool = False,
    key: PRNGKeyArray,
    **kwargs,
):
    """JFB: Solve a fixed-point and backprop through the final explicit step only.

    Its primary purpose is to register custom forward
    and backward differentiation rules (`def_fwd`, `def_bwd`) that implement
    the Jacobian-Free Backpropagation (JFB) algorithm, as described in
    Fung et al. (2021), arXiv:2103.12803.

    The standard approach to backpropagation through a fixed-point solve,
    derived from the Implicit Function Theorem, requires solving a linear
    system involving the Jacobian of the fixed-point mapping. JFB provides
    an approximation that avoids this costly step by treating the converged
    fixed point as a constant during the backward pass.

    Forward API mirrors solvers: returns (u_star, u_prev, tnstep).
    """
    params, Qd = diff_args
    return solver(params, static, Qd, inference=inference, key=key, **kwargs)


@jfb.def_fwd
def jfb_fwd(
    perturbed,
    diff_args,
    static,
    *,
    solver: Callable = picard,
    inference: bool = False,
    key: PRNGKeyArray,
    **kwargs,
):
    """Forward pass: run the solver, then re-evaluate the very last step
    u_star = f(stop_gradient(u_prev), Qd) under inference mode, and cache its VJP.
    """
    params, Qd = diff_args
    u_star, u_prev, tnstep = solver(
        params, static, Qd, inference=inference, key=key, **kwargs
    )

    def final_step(_params, _Qd):
        f = eqx.nn.inference_mode(eqx.combine(_params, static), True)
        return f(jax.lax.stop_gradient(u_prev), _Qd, inference=True, key=key)

    # Recompute the last explicit step and capture VJP
    u_star_final, vjp_fn = eqx.filter_vjp(final_step, params, Qd)

    primals_out = (u_star_final, u_prev, tnstep)
    residuals = vjp_fn
    return primals_out, residuals


@jfb.def_bwd
def jfb_bwd(
    residuals,
    g,
    perturbed,
    diff_args,
    static,
    *,
    solver: Callable = picard,
    inference: bool = False,
    key: PRNGKeyArray,
    **kwargs,
):
    """Backward pass: apply cached VJP of the last explicit step (JFB approximation)."""
    vjp_fn = residuals
    g_u_star, *_ = g

    if g_u_star is None:
        return (None, None)

    grad_params, grad_Qd = vjp_fn(g_u_star)
    return (grad_params, grad_Qd)


@eqx.filter_custom_vjp
def gdeq(
    diff_args,
    static,
    *,
    solver: Callable = broyden,  # must be a Broyden-style solver with return_B
    inference: bool = False,
    key: PRNGKeyArray,
    **kwargs,
):
    """GDEQ: Like JFB but with approximate inverse-Jacobian preconditioning in the adjoint."""
    params, Qd = diff_args
    return solver(params, static, Qd, inference=inference, key=key, **kwargs)


@gdeq.def_fwd
def gdeq_fwd(
    perturbed,
    diff_args,
    static,
    *,
    solver: Callable = broyden,
    inference: bool = False,
    key: PRNGKeyArray,
    **kwargs,
):
    """Forward pass:
    1) Solve with `return_B=True` to capture limited-memory inverse-Jacobian factors.
    2) Recompute the last explicit step u_star = f(stop_gradient(u_prev), Qd)
       under inference mode and cache its VJP.
    """
    params, Qd = diff_args

    u_star, u_prev, tnstep, (Us, VTs, valid_mask) = solver(
        params,
        static,
        Qd,
        return_B=True,
        inference=inference,
        key=key,
        **kwargs,
    )

    def final_step(_params, _Qd):
        f = eqx.nn.inference_mode(eqx.combine(_params, static), True)
        return f(jax.lax.stop_gradient(u_prev), _Qd, inference=True, key=key)

    u_star_final, vjp_fn = eqx.filter_vjp(final_step, params, Qd)

    primals_out = (u_star_final, u_prev, tnstep)
    residuals = (vjp_fn, Us, VTs, valid_mask, u_star_final.shape)
    return primals_out, residuals


@gdeq.def_bwd
def gdeq_bwd(
    residuals,
    g,
    perturbed,
    diff_args,
    static,
    *,
    solver: Callable = broyden,
    **kwargs,
):
    """Backward pass:
    1) Precondition the outgoing adjoint with -B_T^{-T}
    2) Apply the cached VJP of the last explicit step.
    """
    vjp_fn, Us, VTs, valid_mask, out_shape = residuals
    g_u_star, *_ = g

    if g_u_star is None:
        return (None, None)

    # Preconditioning in flat space
    g_u_star_flat = jnp.ravel(g_u_star)
    g_tilde_flat = -masked_rmatvec(g_u_star_flat, Us, VTs, valid_mask)
    g_tilde = jnp.reshape(g_tilde_flat, out_shape)

    grad_params, grad_Qd = vjp_fn(g_tilde)
    return (grad_params, grad_Qd)
