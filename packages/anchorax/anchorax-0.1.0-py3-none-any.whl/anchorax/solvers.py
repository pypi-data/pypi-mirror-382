from functools import partial
from typing import Callable

import equinox as eqx
import jax
import jax.numpy as jnp
import jax.random as jr
from einops import rearrange


def _compute_diffs(u: jax.Array, g_u: jax.Array) -> tuple[jax.Array, jax.Array]:
    """Compute absolute and relative residuals used for stopping and best-so-far."""
    abs_diff = jnp.linalg.norm(jnp.ravel(g_u))
    rel_diff = abs_diff / (jnp.linalg.norm(jnp.ravel(g_u + u)) + 1e-9)
    return abs_diff, rel_diff


def _init_u0(Qd: jax.Array, u0: jax.Array | None) -> jax.Array:
    if u0 is not None:
        assert (_us := u0.shape) == (_Qds := Qd.shape), (
            f"`u0` and `Qd` must have the same shape. Got {_us} and {_Qds}"
        )
        return u0
    return jnp.zeros_like(Qd)


def _empty_B_factors(
    dim: int, LBFGS_thres: int, dtype
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Return zeroed factors for the limited-memory inverse Jacobian approximation.

    With valid_mask=False everywhere, masked_rmatvec(x, ...) = -x (since U=0),
    hence -masked_rmatvec(x, ...) = x, i.e., the identity preconditioner.
    """
    Us = jnp.zeros((dim, LBFGS_thres), dtype=dtype)
    VTs = jnp.zeros((LBFGS_thres, dim), dtype=dtype)
    valid_mask = jnp.zeros((LBFGS_thres,), dtype=jnp.bool_)
    return Us, VTs, valid_mask


@partial(
    jax.jit,
    static_argnames=[
        "static",
        "eps",
        "max_depth",
        "stop_mode",
        "LBFGS_thres",
        "ls",
        "return_final",
        "return_B",
    ],
)
def picard(
    params,
    static,
    Qd: jax.Array,
    *,
    u0: jax.Array | None = None,
    eps: float = 1e-3,
    max_depth: int = 100,
    stop_mode: str = "abs",
    LBFGS_thres: int = 1,
    ls: bool = False,  # present for API compatibility, unused in Picard
    return_final: bool = False,
    return_B: bool = False,
    inference: bool = False,
    key: jax.Array,
    **kwargs,
) -> (
    tuple[jax.Array, jax.Array, jax.Array]
    | tuple[jax.Array, jax.Array, jax.Array, tuple[jax.Array, jax.Array, jax.Array]]
):
    """Naive fixed-point iteration with a homogenized API.

    Solves u* = f(u*, Qd). Residual g(u) = f(u, Qd) - u.
    Stopping criteria and outputs match the Broyden solver for compatibility.
    """
    f = eqx.combine(params, static)
    u = _init_u0(Qd, u0)
    dtype = u.dtype

    # Statistics and best-so-far
    g_u = f(u, Qd, inference=inference, key=jr.fold_in(key, 0)) - u
    abs_diff, rel_diff = _compute_diffs(u, g_u)
    lowest_u = u
    lowest_u_prev = u
    lowest_abs = abs_diff
    lowest_rel = rel_diff

    tnstep = jnp.array(1, dtype=jnp.int32)  # already evaluated f once
    nstep = jnp.array(0, dtype=jnp.int32)

    def cond_fn(state):
        (
            u,
            u_prev,
            g_u,
            nstep,
            tnstep,
            lowest_u,
            lowest_u_prev,
            lowest_abs,
            lowest_rel,
        ) = state
        abs_diff, rel_diff = _compute_diffs(u, g_u)
        current = abs_diff if stop_mode == "abs" else rel_diff
        return jnp.logical_and(current >= eps, nstep < max_depth)

    def body_fn(state):
        (
            u,
            u_prev,
            g_u,
            nstep,
            tnstep,
            lowest_u,
            lowest_u_prev,
            lowest_abs,
            lowest_rel,
        ) = state

        # Picard update: u_next = f(u, Qd)
        u_prev_next = u
        key_iter = jr.fold_in(key, nstep + 1)
        u_next = f(u, Qd, inference=inference, key=key_iter)
        g_next = u_next - u

        # Stats
        abs_diff, rel_diff = _compute_diffs(u_next, g_next)

        # Best-so-far
        is_lowest_abs = abs_diff < lowest_abs
        is_lowest_rel = rel_diff < lowest_rel
        best_now = (
            jnp.where(stop_mode == "abs", is_lowest_abs, is_lowest_rel) | return_final
        )

        lowest_u_prev = jnp.where(best_now, u_prev_next, lowest_u_prev)
        lowest_u = jnp.where(best_now, u_next, lowest_u)
        lowest_abs = jnp.where(is_lowest_abs, abs_diff, lowest_abs)
        lowest_rel = jnp.where(is_lowest_rel, rel_diff, lowest_rel)

        return (
            u_next,
            u_prev_next,
            g_next,
            nstep + 1,
            tnstep + 1,
            lowest_u,
            lowest_u_prev,
            lowest_abs,
            lowest_rel,
        )

    # While-loop
    (
        u_star,
        u_prev,
        g_u,
        nstep,
        tnstep,
        lowest_u,
        lowest_u_prev,
        lowest_abs,
        lowest_rel,
    ) = jax.lax.while_loop(
        cond_fn,
        body_fn,
        (u, u, g_u, nstep, tnstep, lowest_u, lowest_u_prev, lowest_abs, lowest_rel),
    )

    out_u = jax.lax.select(return_final, u_star, lowest_u)
    out_u_prev = jax.lax.select(return_final, u_prev, lowest_u_prev)

    if return_B:
        dim = out_u.size
        Bf = _empty_B_factors(dim, LBFGS_thres, dtype)
        return out_u, out_u_prev, tnstep, Bf
    return out_u, out_u_prev, tnstep


@partial(
    jax.jit,
    static_argnames=[
        "static",
        "eps",
        "max_depth",
        "stop_mode",
        "window_size",
        "reg",
        "mixing_param",
        "restarting",
        "LBFGS_thres",
        "ls",
        "return_final",
        "return_B",
    ],
)
def anderson(
    params,
    static,
    Qd: jax.Array,
    *,
    u0: jax.Array | None = None,
    eps: float = 1e-3,
    max_depth: int = 100,
    stop_mode: str = "abs",
    window_size: int = 2,
    reg: float = 1e-8,
    mixing_param: float = 1.0,
    restarting: bool = False,
    LBFGS_thres: int = 1,
    ls: bool = False,  # present for API compatibility, unused in this Anderson variant
    return_final: bool = False,
    return_B: bool = False,
    inference: bool = False,
    key: jax.Array,
    **kwargs,
) -> (
    tuple[jax.Array, jax.Array, jax.Array]
    | tuple[jax.Array, jax.Array, jax.Array, tuple[jax.Array, jax.Array, jax.Array]]
):
    """Anderson acceleration with homogenized API and stopping logic."""
    assert window_size > 0, "window_size must be positive"
    assert reg >= 0, "reg must be non-negative"
    assert 0 <= mixing_param <= 1, "mixing_param ∈ [0, 1]"

    f = eqx.combine(params, static)
    u = _init_u0(Qd, u0)
    dtype = u.dtype

    buf_size = window_size + 1
    zeros_buf = jnp.zeros((buf_size,) + Qd.shape, dtype=dtype)

    # First evaluation
    u1 = f(u, Qd, inference=inference, key=jr.fold_in(key, 0))
    g0 = u1 - u

    # History buffers
    x_hist = zeros_buf.at[0].set(u)
    gx_hist = zeros_buf.at[0].set(u1)
    res_hist = zeros_buf.at[0].set(g0)

    hist_len = jnp.array(1, dtype=jnp.int32)
    ptr = jnp.array(1, dtype=jnp.int32)

    # Stats and best-so-far
    abs_diff, rel_diff = _compute_diffs(u1, g0)
    lowest_u = u1
    lowest_u_prev = u
    lowest_abs = abs_diff
    lowest_rel = rel_diff

    # Loop state
    init_state = (
        u1,  # u
        u,  # u_prev
        hist_len,
        ptr,
        x_hist,
        gx_hist,
        res_hist,
        jnp.array(1, dtype=jnp.int32),  # tnstep
        jnp.array(1, dtype=jnp.int32),  # nstep
        lowest_u,
        lowest_u_prev,
        lowest_abs,
        lowest_rel,
        g0,  # g_u at current u
    )

    def cond_fn(state):
        u = state[0]
        nstep = state[8]
        g_u = state[13]  # current residual g(u)
        abs_diff, rel_diff = _compute_diffs(u, g_u)
        current = jax.lax.select(stop_mode == "abs", abs_diff, rel_diff)
        return jnp.logical_and(current >= eps, nstep < max_depth)

    def body_fn(state):
        (
            u,
            u_prev,
            hist_len,
            ptr,
            x_hist,
            gx_hist,
            res_hist,
            tnstep,
            nstep,
            lowest_u,
            lowest_u_prev,
            lowest_abs,
            lowest_rel,
            _,
        ) = state

        # Evaluate at current u
        key_iter = jr.fold_in(key, nstep)
        gu = f(u, Qd, inference=inference, key=key_iter)
        r = gu - u

        # Update history
        x_hist = x_hist.at[ptr].set(u)
        gx_hist = gx_hist.at[ptr].set(gu)
        res_hist = res_hist.at[ptr].set(r)

        ptr = (ptr + 1) % buf_size
        hist_len = jnp.minimum(hist_len + 1, buf_size)

        # Build masked residual matrix Ft ∈ R^{m×D} (flattened)
        valid = jnp.arange(buf_size) < hist_len  # shape (buf_size,)
        Ft = rearrange(res_hist, "m ... -> m (...)")
        Ft = Ft * valid[:, None]

        # Solve alpha = argmin ||F^T alpha|| with simplex-like constraint sum alpha = 1
        RR = Ft @ Ft.T + reg * jnp.eye(buf_size, dtype=Ft.dtype)
        b = valid.astype(Ft.dtype)
        alpha = jnp.linalg.solve(RR, b)
        alpha = alpha * valid
        alpha = alpha / (alpha.sum() + 1e-12)

        x_interp = jnp.einsum("m,m...->...", alpha, x_hist)
        gx_interp = jnp.einsum("m,m...->...", alpha, gx_hist)
        u_next = (1 - mixing_param) * x_interp + mixing_param * gx_interp

        # Optional restart when buffer is full
        restarting_now = jnp.logical_and(restarting, hist_len == buf_size)
        x_hist, gx_hist, res_hist, hist_len, ptr = jax.lax.cond(
            restarting_now,
            lambda _: (
                zeros_buf.at[0].set(u),
                zeros_buf.at[0].set(gu),
                zeros_buf.at[0].set(r),
                jnp.array(1, jnp.int32),
                jnp.array(1, jnp.int32),
            ),
            lambda _: (x_hist, gx_hist, res_hist, hist_len, ptr),
            operand=None,
        )

        # Stats and best-so-far based on consistent residual at u_next
        g_next = (
            f(u_next, Qd, inference=inference, key=jr.fold_in(key, nstep + 1)) - u_next
        )
        abs_diff, rel_diff = _compute_diffs(u_next, g_next)

        is_lowest_abs = abs_diff < lowest_abs
        is_lowest_rel = rel_diff < lowest_rel
        best_now = (
            jnp.where(stop_mode == "abs", is_lowest_abs, is_lowest_rel) | return_final
        )

        lowest_u_prev = jnp.where(best_now, u, lowest_u_prev)
        lowest_u = jnp.where(best_now, u_next, lowest_u)
        lowest_abs = jnp.where(is_lowest_abs, abs_diff, lowest_abs)
        lowest_rel = jnp.where(is_lowest_rel, rel_diff, lowest_rel)

        return (
            u_next,
            u,
            hist_len,
            ptr,
            x_hist,
            gx_hist,
            res_hist,
            tnstep
            + 2,  # we called f twice this iteration (gu and g_next); conservative count
            nstep + 1,
            lowest_u,
            lowest_u_prev,
            lowest_abs,
            lowest_rel,
            g_next,
        )

    final_state = jax.lax.while_loop(cond_fn, body_fn, init_state)

    (
        u_star,
        u_prev,
        _hist_len,
        _ptr,
        _xh,
        _gxh,
        _rh,
        tnstep,
        _nstep,
        lowest_u,
        lowest_u_prev,
        _lowest_abs,
        _lowest_rel,
        _g_last,
    ) = final_state

    out_u = jax.lax.select(return_final, u_star, lowest_u)
    out_u_prev = jax.lax.select(return_final, u_prev, lowest_u_prev)

    if return_B:
        dim = out_u.size
        Bf = _empty_B_factors(dim, LBFGS_thres, dtype)
        return out_u, out_u_prev, tnstep, Bf
    return out_u, out_u_prev, tnstep


def armijo_line_search(
    update: jax.Array,
    x0: jax.Array,
    g0: jax.Array,
    g_func: Callable,
    *,
    on: bool = True,
    c1: float = 1e-4,
    alpha0: float = 1.0,
    amin: float = 0.0,
    key: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array, jax.Array, jax.Array]:
    """Armijo backtracking line search. Pure and JIT-compatible.

    Returns (x_est, g_new, delta_x, delta_g, n_iters).
    """
    phi0 = jnp.dot(g0, g0)
    derphi0 = -phi0

    def perform_search():
        x_est_a0 = x0 + alpha0 * update
        g_a0 = g_func(x_est_a0, key)
        phi_a0 = jnp.dot(g_a0, g_a0)

        armijo_ok0 = phi_a0 <= phi0 + c1 * alpha0 * derphi0

        def return_alpha0():
            n_iters = jnp.array(0, dtype=jnp.int32)
            return alpha0, x_est_a0, g_a0, n_iters

        def interpolate():
            alpha1 = -derphi0 * alpha0**2 / 2.0 / (phi_a0 - phi0 - derphi0 * alpha0)
            x_est_a1 = x0 + alpha1 * update
            g_a1 = g_func(x_est_a1, jr.fold_in(key, 0))
            phi_a1 = jnp.dot(g_a1, g_a1)

            init_state = (
                alpha0,
                alpha1,
                phi_a0,
                phi_a1,
                g_a1,
                jnp.array(False, dtype=jnp.bool_),
                jnp.array(1, dtype=jnp.int32),
            )

            def cond_fn(state):
                _, alpha_curr, _, _, _, satisfied, _ = state
                return jnp.logical_and(alpha_curr > amin, jnp.logical_not(satisfied))

            def body_fn(state):
                alpha_prev, alpha_curr, phi_prev, phi_curr, _, _, it = state

                factor = alpha_prev**2 * alpha_curr**2 * (alpha_curr - alpha_prev)
                a = alpha_prev**2 * (
                    phi_curr - phi0 - derphi0 * alpha_curr
                ) - alpha_curr**2 * (phi_prev - phi0 - derphi0 * alpha_prev)
                a = a / factor
                b = -(alpha_prev**3) * (
                    phi_curr - phi0 - derphi0 * alpha_curr
                ) + alpha_curr**3 * (phi_prev - phi0 - derphi0 * alpha_prev)
                b = b / factor

                alpha_next = (-b + jnp.sqrt(jnp.abs(b**2 - 3 * a * derphi0))) / (
                    3.0 * a
                )
                is_bad_interp = ((alpha_curr - alpha_next) > alpha_curr / 2.0) | (
                    (1 - alpha_next / alpha_curr) < 0.96
                )
                alpha_next = jnp.where(is_bad_interp, alpha_curr / 2.0, alpha_next)

                x_est_next = x0 + alpha_next * update
                g_next = g_func(x_est_next, jr.fold_in(key, it))
                phi_next = jnp.dot(g_next, g_next)
                satisfied = phi_next <= phi0 + c1 * alpha_next * derphi0
                alpha_next = jnp.maximum(amin, alpha_next)

                return (
                    alpha_curr,
                    alpha_next,
                    phi_curr,
                    phi_next,
                    g_next,
                    satisfied,
                    it + 1,
                )

            (_, alpha_star, _, _, g_star, _, n_iters) = jax.lax.while_loop(
                cond_fn, body_fn, init_state
            )
            x_est_star = x0 + alpha_star * update
            return alpha_star, x_est_star, g_star, n_iters

        s, x_est, g_new, n_iters = jax.lax.cond(armijo_ok0, return_alpha0, interpolate)
        return s, x_est, g_new, n_iters

    def bypass_search():
        s = 1.0
        x_est = x0 + s * update
        g_new = g_func(x_est, jr.fold_in(key, 0))
        n_iters = jnp.array(0, dtype=jnp.int32)
        return s, x_est, g_new, n_iters

    s, x_est, g_new, n_iters = jax.lax.cond(on, perform_search, bypass_search)
    delta_x = x_est - x0
    delta_g = g_new - g0
    return x_est, g_new, delta_x, delta_g, n_iters


def masked_matvec(
    x: jax.Array, Us: jax.Array, VTs: jax.Array, valid_mask: jax.Array
) -> jax.Array:
    """Compute (-I + U Vᵀ) x with masked history (unbatched)."""
    VTx = jnp.einsum("ld, d -> l", VTs, x)
    Us_masked = Us * valid_mask  # broadcast over columns
    UVTx = jnp.einsum("dl, l -> d", Us_masked, VTx)
    return -x + UVTx


def masked_rmatvec(
    x: jax.Array, Us: jax.Array, VTs: jax.Array, valid_mask: jax.Array
) -> jax.Array:
    """Compute xᵀ(-I + U Vᵀ) (right-matvec) with masked history (unbatched)."""
    Us_masked = Us * valid_mask
    xTU = jnp.einsum("d, dl -> l", x, Us_masked)
    xTUVT = jnp.einsum("l, ld -> d", xTU, VTs)
    return -x + xTUVT


@partial(
    jax.jit,
    static_argnames=[
        "static",
        "eps",
        "max_depth",
        "stop_mode",
        "LBFGS_thres",
        "ls",
        "return_final",
        "return_B",
    ],
)
def broyden(
    params,
    static,
    Qd: jax.Array,
    *,
    u0: jax.Array | None = None,
    eps: float = 1e-3,
    max_depth: int = 50,
    stop_mode: str = "abs",
    LBFGS_thres: int | None = 3,
    ls: bool = False,
    return_final: bool = False,
    return_B: bool = False,
    inference: bool = False,
    key: jax.Array,
    **kwargs,
):
    """Broyden’s method with limited-memory inverse Jacobian approximation.

    Matches the homogenized API and outputs.
    """
    f = eqx.combine(params, static)
    u0 = _init_u0(Qd, u0)
    original_shape = u0.shape
    u0_flat = jnp.ravel(u0)
    dim = u0_flat.shape[0]

    def g(u_flat, _key):
        return (
            f(u_flat.reshape(original_shape), Qd, inference=inference, key=_key).ravel()
            - u_flat
        )

    LBFGS_thres = max_depth if LBFGS_thres is None else LBFGS_thres

    x_est = u0_flat
    gx = g(x_est, key)

    Us = jnp.zeros((dim, LBFGS_thres), dtype=u0.dtype)
    VTs = jnp.zeros((LBFGS_thres, dim), dtype=u0.dtype)
    valid_mask = jnp.zeros(LBFGS_thres, dtype=jnp.bool_)

    update = gx  # initial unpreconditioned direction

    init_abs_diff = jnp.linalg.norm(gx)
    init_rel_diff = init_abs_diff / (jnp.linalg.norm(gx + x_est) + 1e-9)

    current0 = jax.lax.select(stop_mode == "abs", init_abs_diff, init_rel_diff)
    done0 = jnp.logical_and(current0 < eps, jnp.logical_not(jnp.array(return_final)))

    init_state = (
        x_est,  # current
        x_est,  # prev
        gx,  # residual
        update,  # update dir
        Us,
        VTs,
        valid_mask,
        jnp.array(0, dtype=jnp.int32),  # nstep
        jnp.array(0, dtype=jnp.int32),  # tnstep
        x_est,  # lowest_x
        x_est,  # lowest_prev_x
        init_abs_diff,
        init_rel_diff,
        done0,  # done
        Us,
        VTs,
        valid_mask,  # best factors (aligned with best solution)
    )

    def cond_fn(state):
        _, _, _, _, _, _, _, nstep, _, _, _, _, _, done, *_ = state
        return jnp.logical_and(nstep < max_depth, jnp.logical_not(done))

    def body_fn(state):
        (
            x_est_curr,
            _x_prev,
            gx,
            update,
            Us,
            VTs,
            valid_mask,
            nstep,
            tnstep,
            lowest_xest,
            lowest_xest_prev,
            lowest_abs_diff,
            lowest_rel_diff,
            _done,
            best_Us,
            best_VTs,
            best_mask,
        ) = state

        x_est, gx, delta_x, delta_gx, ite = armijo_line_search(
            update, x_est_curr, gx, g, key=jr.fold_in(key, nstep), on=ls, amin=1e-2
        )
        tnstep = tnstep + ite + 1

        abs_diff = jnp.linalg.norm(gx)
        rel_diff = abs_diff / (jnp.linalg.norm(gx + x_est) + 1e-9)

        is_lowest_abs = abs_diff < lowest_abs_diff
        is_lowest_rel = rel_diff < lowest_rel_diff
        is_best = (
            jnp.where(stop_mode == "abs", is_lowest_abs, is_lowest_rel) | return_final
        )

        lowest_xest_prev, lowest_xest, best_Us, best_VTs, best_mask = jax.lax.cond(
            is_best,
            lambda _: (x_est_curr, x_est, Us, VTs, valid_mask),
            lambda _: (lowest_xest_prev, lowest_xest, best_Us, best_VTs, best_mask),
            operand=None,
        )
        lowest_abs_diff = jnp.where(is_lowest_abs, abs_diff, lowest_abs_diff)
        lowest_rel_diff = jnp.where(is_lowest_rel, rel_diff, lowest_rel_diff)

        current_diff = jax.lax.select(stop_mode == "abs", abs_diff, rel_diff)
        converged = current_diff < eps
        done = converged & jnp.logical_not(return_final)

        # L-BFGS-style rank-1 update of inverse-Jacobian factors
        idx = nstep % LBFGS_thres

        vT = masked_rmatvec(delta_x, Us, VTs, valid_mask)
        vT_delta_gx = jnp.dot(vT, delta_gx)

        matvec_delta_gx = masked_matvec(delta_gx, Us, VTs, valid_mask)
        u_num = delta_x - matvec_delta_gx
        u = u_num / (vT_delta_gx + 1e-9)

        vT = jnp.nan_to_num(vT, nan=0.0, posinf=0.0, neginf=0.0)
        u = jnp.nan_to_num(u, nan=0.0, posinf=0.0, neginf=0.0)

        Us = Us.at[:, idx].set(u)
        VTs = VTs.at[idx, :].set(vT)
        valid_mask = valid_mask.at[idx].set(True)

        next_update = -masked_matvec(gx, Us, VTs, valid_mask)

        return (
            x_est,
            x_est_curr,
            gx,
            next_update,
            Us,
            VTs,
            valid_mask,
            nstep + 1,
            tnstep,
            lowest_xest,
            lowest_xest_prev,
            lowest_abs_diff,
            lowest_rel_diff,
            done,
            best_Us,
            best_VTs,
            best_mask,
        )

    final_state = jax.lax.while_loop(cond_fn, body_fn, init_state)

    (
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        nstep,
        tnstep,
        lowest_xest,
        lowest_xest_prev,
        _lowest_abs_diff,
        _lowest_rel_diff,
        _,
        best_Us,
        best_VTs,
        best_mask,
    ) = final_state

    u_star = lowest_xest.reshape(original_shape)
    u_prev = lowest_xest_prev.reshape(original_shape)

    if return_B:
        return u_star, u_prev, tnstep, (best_Us, best_VTs, best_mask)
    return u_star, u_prev, tnstep
