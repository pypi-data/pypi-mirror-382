from abc import abstractmethod
from dataclasses import field

from plum import dispatch

import equinox as eqx
import jax
import jax.experimental.sparse as jsparse
import jax.lax as lax
import jax.nn as nn
import jax.numpy as jnp
import lineax as lx

from jax.scipy.special import logit
from jaxtyping import Array

from .common import ModelParams
from .sparse import SparseMatrix
from .utils import kl_discrete


def _update_sparse_beta(gdx, carry):
    ZrG, gsq_diag, params = carry

    # (t x k) (k x t)
    mean_beta_g = params.mean_beta[gdx] * params.p_hat.T[gdx]

    # add gth effect back across all K dim
    ZrG = ZrG.at[:, gdx].set(ZrG[:, gdx] + gsq_diag[gdx] * mean_beta_g)

    var_beta_g = jnp.reciprocal(params.tau_beta + gsq_diag[gdx])
    mean_beta_g = ZrG[:, gdx] * var_beta_g

    eps = 1e-8
    p_hat_g = nn.sigmoid(logit(params.p[gdx]) + 0.5 * (mean_beta_g**2) / var_beta_g)
    p_hat_g = jnp.clip(p_hat_g, eps, 1 - eps)

    # residualize based on newest estimates for downstream inf
    ZrG = ZrG.at[:, gdx].set(ZrG[:, gdx] - gsq_diag[gdx] * (mean_beta_g * p_hat_g))
    params = params._replace(
        mean_beta=params.mean_beta.at[gdx].set(mean_beta_g),
        var_beta=params.var_beta.at[gdx].set(var_beta_g),
        p_hat=params.p_hat.at[:, gdx].set(p_hat_g),
    )

    return ZrG, gsq_diag, params


@dispatch
def _get_diag(G: Array) -> Array:
    return jnp.sum(G**2, axis=0)


@dispatch
def _get_diag(G: SparseMatrix) -> Array:
    return jsparse.sparsify(jnp.sum)(G.matrix**2, axis=0).todense()  # type: ignore


@dispatch
def _wgt_sumsq(G: SparseMatrix, vector: Array) -> Array:
    tmp = G.matrix * vector
    return jsparse.sparsify(jnp.sum)(tmp**2)  # type: ignore


@dispatch
def _wgt_sumsq(G: Array, vector: Array) -> Array:
    tmp = G * vector
    return jnp.sum(tmp**2)


_multi_linear_solve = eqx.filter_vmap(lx.linear_solve, in_axes=(None, 1, None))


@dispatch
def _update_dense_beta(G: Array, params: ModelParams) -> ModelParams:
    # Create linear operator on G
    G_op = lx.MatrixLinearOperator(G)

    # Use lineax's CG solver
    solver = lx.NormalCG(rtol=1e-6, atol=1e-6)
    out = _multi_linear_solve(G_op, params.mean_z, solver)

    # Updated beta
    updated_beta = out.value.T

    return params._replace(mean_beta=updated_beta)


@dispatch
def _update_dense_beta(G: SparseMatrix, params: ModelParams) -> ModelParams:
    # Use lineax's CG solver
    solver = lx.NormalCG(rtol=1e-6, atol=1e-6)

    out = jax.vmap(lambda b: lx.linear_solve(G, b, solver), in_axes=1)(params.mean_z)

    # Updated beta
    updated_beta = out.value.T
    return params._replace(mean_beta=updated_beta)


class GuideModel(eqx.Module):
    guide_data: Array | SparseMatrix
    gsq_diag: Array = field(init=False)

    def __post_init__(self):
        self.gsq_diag = _get_diag(self.guide_data)  # type: ignore

    @property
    def shape(self):
        return self.guide_data.shape

    @abstractmethod
    def weighted_sumsq(self, params: ModelParams) -> Array: ...

    @abstractmethod
    def predict(self, params: ModelParams) -> Array: ...

    @abstractmethod
    def update(self, params: ModelParams) -> ModelParams: ...

    @staticmethod
    @abstractmethod
    def update_hyperparam(params: ModelParams) -> ModelParams: ...

    @staticmethod
    @abstractmethod
    def kl_divergence(params: ModelParams) -> Array: ...


class SparseGuideModel(GuideModel):
    def predict(self, params: ModelParams) -> Array:
        return self.guide_data @ (params.mean_beta * params.p_hat.T)

    def weighted_sumsq(self, params: ModelParams) -> Array:
        mean_bb = jnp.sum((params.mean_beta**2 + params.var_beta) * params.p_hat.T, axis=1)
        return _wgt_sumsq(self.guide_data, jnp.sqrt(mean_bb))

    def update(self, params: ModelParams) -> ModelParams:
        # compute E[Z'k]G: remove the g-th effect

        # remove predicted mean
        pred = self.predict(params)
        ZrG = (params.mean_z - pred).T @ self.guide_data

        _, g_dim = params.mean_beta.shape
        _, _, params = lax.fori_loop(0, g_dim, _update_sparse_beta, (ZrG, self.gsq_diag, params))

        return params

    @staticmethod
    def update_hyperparam(params: ModelParams) -> ModelParams:
        est_var_beta = params.mean_beta**2 + params.var_beta
        u_tau_beta = jnp.sum(params.p_hat, axis=-1) / jnp.sum(est_var_beta * params.p_hat.T, axis=0)

        return params._replace(tau_beta=u_tau_beta)

    @staticmethod
    def kl_divergence(params: ModelParams) -> Array:
        # KL for each beta
        kl_beta = 0.5 * (
            (params.mean_beta**2 + params.var_beta) * params.tau_beta
            - 1
            - jnp.log(params.var_beta)
            - jnp.log(params.tau_beta)
        )
        # sum them up, weighted by posterior prob of having an effect
        kl_beta = jnp.sum(params.p_hat.T * kl_beta)

        # KL for eta selection variables
        kl_eta = kl_discrete(params.p_hat, params.p)
        return kl_beta + kl_eta


class DenseGuideModel(GuideModel):
    def predict(self, params: ModelParams) -> Array:
        return self.guide_data @ params.mean_beta

    def weighted_sumsq(self, params: ModelParams) -> Array:
        pred_z = self.predict(params)
        return jnp.sum(pred_z**2)

    def update(self, params: ModelParams) -> ModelParams:
        return _update_dense_beta(self.guide_data, params)

    @staticmethod
    def update_hyperparam(params: ModelParams) -> ModelParams:
        return params

    @staticmethod
    def kl_divergence(params: ModelParams) -> Array:
        return jnp.asarray(0.0)
