import os
import multiprocessing
import warnings
from math import ceil, floor
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union, cast, Dict, Any

import numpy as np
import pandas as pd
from scipy.linalg import solve  # type: ignore
from scipy.optimize import minimize  # type: ignore
from scipy.special import gammaln  # type: ignore
from scipy.special import polygamma  # type: ignore
from scipy.stats import norm  # type: ignore
from sklearn.linear_model import LinearRegression  # type: ignore

from deconveil.grid_search import grid_fit_beta
from pydeseq2.utils import fit_alpha_mle
from pydeseq2.utils import get_num_processes
from pydeseq2.grid_search import grid_fit_alpha
from pydeseq2.grid_search import grid_fit_shrink_beta


def irls_glm(
    counts: np.ndarray,
    cnv: np.ndarray,
    size_factors: np.ndarray,
    design_matrix: np.ndarray,
    disp: float,
    min_mu: float = 0.5,
    beta_tol: float = 1e-8,
    min_beta: float = -30,
    max_beta: float = 30,
    optimizer: Literal["BFGS", "L-BFGS-B"] = "L-BFGS-B",
    maxiter: int = 250,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, bool]:

    assert optimizer in ["BFGS", "L-BFGS-B"]
    
    num_vars = design_matrix.shape[1]
    X = design_matrix
    
    # if full rank, estimate initial betas for IRLS below
    if np.linalg.matrix_rank(X) == num_vars:
        Q, R = np.linalg.qr(X)
        y = np.log((counts / cnv) / size_factors + 0.1)
        beta_init = solve(R, Q.T @ y)
        beta = beta_init

    else:  # Initialise intercept with log base mean
        beta_init = np.zeros(num_vars)
        beta_init[0] = np.log((counts / cnv) / size_factors).mean()
        beta = beta_init
        
    dev = 1000.0
    dev_ratio = 1.0

    ridge_factor = np.diag(np.repeat(1e-6, num_vars))
    mu = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
    
    converged = True
    i = 0
    while dev_ratio > beta_tol:
        W = mu / (1.0 + mu * disp)
        z = np.log((mu / cnv) / size_factors) + (counts - mu) / mu
        H = (X.T * W) @ X + ridge_factor
        beta_hat = solve(H, X.T @ (W * z), assume_a="pos")
        i += 1

        if sum(np.abs(beta_hat) > max_beta) > 0 or i >= maxiter:
            # If IRLS starts diverging, use L-BFGS-B
            def f(beta: np.ndarray) -> float:
                # closure to minimize
                mu_ = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
                
                return nb_nll(counts, mu_, disp) + 0.5 * (ridge_factor @ beta**2).sum()

            def df(beta: np.ndarray) -> np.ndarray:
                mu_ = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
                return (
                    -X.T @ counts
                    + ((1 / disp + counts) * mu_ / (1 / disp + mu_)) @ X
                    + ridge_factor @ beta
                )

            res = minimize(
                f,
                beta_init,
                jac=df,
                method=optimizer,
                bounds=(
                    [(min_beta, max_beta)] * num_vars
                    if optimizer == "L-BFGS-B"
                    else None
                ),
            )
            
            beta = res.x
            mu = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
            converged = res.success

        beta = beta_hat
        mu = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
        
        # Compute deviation
        old_dev = dev
        # Replaced deviation with -2 * nll, as in the R code
        dev = -2 * nb_nll(counts, mu, disp)
        dev_ratio = np.abs(dev - old_dev) / (np.abs(dev) + 0.1)

    # Compute H diagonal (useful for Cook distance outlier filtering)
    W = mu / (1.0 + mu * disp)
    W_sq = np.sqrt(W)
    XtWX = (X.T * W) @ X + ridge_factor
    H = W_sq * np.diag(X @ np.linalg.inv(XtWX) @ X.T) * W_sq
    
    # Return an UNthresholded mu 
    # Previous quantities are estimated with a threshold though
    mu = np.maximum(cnv * size_factors * np.exp(np.clip(X @ beta, -30, 30)), min_mu)
    
    return beta, mu, H, converged


def fit_lin_mu(
    counts: np.ndarray,
    size_factors: np.ndarray,
    design_matrix: np.ndarray,
    min_mu: float = 0.5,
) -> np.ndarray:
    """Estimate mean of negative binomial model using a linear regression.

    Used to initialize genewise dispersion models.

    Parameters
    ----------
    counts : ndarray
        Raw counts for a given gene.

    size_factors : ndarray
        Sample-wise scaling factors (obtained from median-of-ratios).

    design_matrix : ndarray
        Design matrix.

    min_mu : float
        Lower threshold for fitted means, for numerical stability. (default: ``0.5``).

    Returns
    -------
    ndarray
        Estimated mean.
    """
    reg = LinearRegression(fit_intercept=False)
    reg.fit(design_matrix, counts / size_factors)
    mu_hat = size_factors * reg.predict(design_matrix)
    # Threshold mu_hat as 1/mu_hat will be used later on.
    return np.maximum(mu_hat, min_mu)


def fit_rough_dispersions(
    normed_counts: np.ndarray, design_matrix: pd.DataFrame
) -> np.ndarray:
    """Rough dispersion estimates from linear model, as per the R code.

    Used as initial estimates in :meth:`DeseqDataSet.fit_genewise_dispersions()
    <pydeseq2.dds.DeseqDataSet.fit_genewise_dispersions>`.

    Parameters
    ----------
    normed_counts : ndarray
        Array of deseq2-normalized read counts. Rows: samples, columns: genes.

    design_matrix : pandas.DataFrame
        A DataFrame with experiment design information (to split cohorts).
        Indexed by sample barcodes. Unexpanded, *with* intercept.

    Returns
    -------
    ndarray
        Estimated dispersion parameter for each gene.
    """
    num_samples, num_vars = design_matrix.shape
    # This method is only possible when num_samples > num_vars.
    # If this is not the case, throw an error.
    if num_samples == num_vars:
        raise ValueError(
            "The number of samples and the number of design variables are "
            "equal, i.e., there are no replicates to estimate the "
            "dispersion. Please use a design with fewer variables."
        )

    reg = LinearRegression(fit_intercept=False)
    reg.fit(design_matrix, normed_counts)
    y_hat = reg.predict(design_matrix)
    y_hat = np.maximum(y_hat, 1)
    alpha_rde = (
        ((normed_counts - y_hat) ** 2 - y_hat) / ((num_samples - num_vars) * y_hat**2)
    ).sum(0)
    return np.maximum(alpha_rde, 0)


def fit_moments_dispersions2(
    normed_counts: np.ndarray, size_factors: np.ndarray
) -> np.ndarray:
    """Dispersion estimates based on moments, as per the R code.

    Used as initial estimates in :meth:`DeseqDataSet.fit_genewise_dispersions()
    <pydeseq2.dds.DeseqDataSet.fit_genewise_dispersions>`.

    Parameters
    ----------
    normed_counts : ndarray
        Array of deseq2-normalized read counts. Rows: samples, columns: genes.

    size_factors : ndarray
        DESeq2 normalization factors.

    Returns
    -------
    ndarray
        Estimated dispersion parameter for each gene.
    """
    # Exclude genes with all zeroes
    #normed_counts = normed_counts[:, ~(normed_counts == 0).all(axis=0)]
    # mean inverse size factor
    s_mean_inv = (1 /size_factors).mean()
    mu = normed_counts.mean(0)
    sigma = normed_counts.var(0, ddof=1)
    # ddof=1 is to use an unbiased estimator, as in R
    # NaN (variance = 0) are replaced with 0s
    return np.nan_to_num((sigma - s_mean_inv * mu) / mu**2)


def nb_nll(
    counts: np.ndarray, mu: np.ndarray, alpha: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    r"""Neg log-likelihood of a negative binomial of parameters ``mu`` and ``alpha``.

    Mathematically, if ``counts`` is a vector of counting entries :math:`y_i`
    then the likelihood of each entry :math:`y_i` to be drawn from a negative
    binomial :math:`NB(\mu, \alpha)` is [1]

    .. math::
        p(y_i | \mu, \alpha) = \frac{\Gamma(y_i + \alpha^{-1})}{
            \Gamma(y_i + 1)\Gamma(\alpha^{-1})
        }
        \left(\frac{1}{1 + \alpha \mu} \right)^{1/\alpha}
        \left(\frac{\mu}{\alpha^{-1} + \mu} \right)^{y_i}

    As a consequence, assuming there are :math:`n` entries,
    the total negative log-likelihood for ``counts`` is

    .. math::
        \ell(\mu, \alpha) = \frac{n}{\alpha} \log(\alpha) +
            \sum_i \left \lbrace
            - \log \left( \frac{\Gamma(y_i + \alpha^{-1})}{
            \Gamma(y_i + 1)\Gamma(\alpha^{-1})
        } \right)
        + (\alpha^{-1} + y_i) \log (\alpha^{-1} + \mu)
        - y_i \log \mu
            \right \rbrace

    This is implemented in this function.

    Parameters
    ----------
    counts : ndarray
        Observations.

    mu : ndarray
        Mean of the distribution :math:`\mu`.

    alpha : float or ndarray
        Dispersion of the distribution :math:`\alpha`,
        s.t. the variance is :math:`\mu + \alpha \mu^2`.

    Returns
    -------
    float or ndarray
        Negative log likelihood of the observations counts
        following :math:`NB(\mu, \alpha)`.

    Notes
    -----
    [1] https://en.wikipedia.org/wiki/Negative_binomial_distribution
    """
    n = len(counts)
    alpha_neg1 = 1 / alpha
    logbinom = gammaln(counts + alpha_neg1) - gammaln(counts + 1) - gammaln(alpha_neg1)
    if hasattr(alpha, "__len__") and len(alpha) > 1:
        return (
            alpha_neg1 * np.log(alpha)
            - logbinom
            + (counts + alpha_neg1) * np.log(mu + alpha_neg1)
            - (counts * np.log(mu))
        ).sum(0)
    else:
        return (
            n * alpha_neg1 * np.log(alpha)
            + (
                -logbinom
                + (counts + alpha_neg1) * np.log(alpha_neg1 + mu)
                - counts * np.log(mu)
            ).sum()
        )


def nbinomGLM(
    design_matrix: np.ndarray,
    counts: np.ndarray,
    cnv: np.ndarray,
    size: np.ndarray,
    offset: np.ndarray,
    prior_no_shrink_scale: float,
    prior_scale: float,
    optimizer="L-BFGS-B",
    shrink_index: int = 1,
) -> Tuple[np.ndarray, np.ndarray, bool]:
    """Fit a negative binomial MAP LFC using an apeGLM prior.

    Only the LFC is shrinked, and not the intercept.

    Parameters
    ----------
    design_matrix : ndarray
        Design matrix.

    counts : ndarray
        Raw counts.

    size : ndarray
        Size parameter of NB family (inverse of dispersion).

    offset : ndarray
        Natural logarithm of size factor.

    prior_no_shrink_scale : float
        Prior variance for the intercept.

    prior_scale : float
        Prior variance for the LFC parameter.

    optimizer : str
        Optimizing method to use in case IRLS starts diverging.
        Accepted values: 'L-BFGS-B', 'BFGS' or 'Newton-CG'. (default: ``'Newton-CG'``).

    shrink_index : int
        Index of the LFC coordinate to shrink. (default: ``1``).

    Returns
    -------
    beta: ndarray
        2-element array, containing the intercept (first) and the LFC (second).

    inv_hessian: ndarray
        Inverse of the Hessian of the objective at the estimated MAP LFC.

    converged: bool
        Whether L-BFGS-B converged.
    """
    num_vars = design_matrix.shape[-1]

    shrink_mask = np.zeros(num_vars)
    shrink_mask[shrink_index] = 1
    no_shrink_mask = np.ones(num_vars) - shrink_mask

    beta_init = np.ones(num_vars) * 0.1 * (-1) ** (np.arange(num_vars))

    # Set optimization scale
    scale_cnst = nbinomFn(
        np.zeros(num_vars),
        design_matrix,
        counts,
        cnv,
        size,
        offset,
        prior_no_shrink_scale,
        prior_scale,
        shrink_index,
    )
    scale_cnst = np.maximum(scale_cnst, 1)

    def f(beta: np.ndarray, cnst: float = scale_cnst) -> float:
        # Function to optimize
        return (
            nbinomFn(
                beta,
                design_matrix,
                counts,
                cnv,
                size,
                offset,
                prior_no_shrink_scale,
                prior_scale,
                shrink_index,
            )
            / cnst
        )

    def df(beta: np.ndarray, cnst: float = scale_cnst) -> np.ndarray:
        # Gradient of the function to optimize
        xbeta = design_matrix @ beta
        d_neg_prior = (
            beta * no_shrink_mask / prior_no_shrink_scale**2
            + 2 * beta * shrink_mask / (prior_scale**2 + beta[shrink_index] ** 2),
        )
        d_nll = (
            counts - (counts + size) / (1 + size * np.exp(-xbeta - offset - cnv))
        ) @ design_matrix

        return (d_neg_prior - d_nll) / cnst

    def ddf(beta: np.ndarray, cnst: float = scale_cnst) -> np.ndarray:
        # Hessian of the function to optimize
        # Note: will only work if there is a single shrink index
        xbeta = design_matrix @ beta
        exp_xbeta_off = np.exp(xbeta + offset + cnv)
        frac = (counts + size) * size * exp_xbeta_off / (size + exp_xbeta_off) ** 2
        # Build diagonal
        h11 = 1 / prior_no_shrink_scale**2
        h22 = (
            2
            * (prior_scale**2 - beta[shrink_index] ** 2)
            / (prior_scale**2 + beta[shrink_index] ** 2) ** 2
        )

        h = np.diag(no_shrink_mask * h11 + shrink_mask * h22)

        return 1 / cnst * ((design_matrix.T * frac) @ design_matrix + np.diag(h))

    res = minimize(
        f,
        beta_init,
        jac=df,
        hess=ddf if optimizer == "Newton-CG" else None,
        method=optimizer,
    )

    beta = res.x
    converged = res.success

    if not converged and num_vars == 2:
        # If the solver failed, fit using grid search (slow)
        # Only for single-factor analysis
        beta = grid_fit_shrink_beta(
            counts,
            cnv,
            offset,
            design_matrix,
            size,
            prior_no_shrink_scale,
            prior_scale,
            scale_cnst,
            grid_length=60,
            min_beta=-30,
            max_beta=30,
        )

    inv_hessian = np.linalg.inv(ddf(beta, 1))

    return beta, inv_hessian, converged
    

def nbinomFn(
    beta: np.ndarray,
    design_matrix: np.ndarray,
    counts: np.ndarray,
    cnv: np.ndarray,
    size: np.ndarray,
    offset: np.ndarray,
    prior_no_shrink_scale: float,
    prior_scale: float,
    shrink_index: int = 1,
) -> float:
    """Return the NB negative likelihood with apeGLM prior.

    Use for LFC shrinkage.

    Parameters
    ----------
    beta : ndarray
        2-element array: intercept and LFC coefficients.

    design_matrix : ndarray
        Design matrix.

    counts : ndarray
        Raw counts.

    size : ndarray
        Size parameter of NB family (inverse of dispersion).

    offset : ndarray
        Natural logarithm of size factor.

    prior_no_shrink_scale : float
        Prior variance for the intercept.

    prior_scale : float
        Prior variance for the intercept.

    shrink_index : int
        Index of the LFC coordinate to shrink. (default: ``1``).

    Returns
    -------
    float
        Sum of the NB negative likelihood and apeGLM prior.
    """
    num_vars = design_matrix.shape[-1]

    shrink_mask = np.zeros(num_vars)
    shrink_mask[shrink_index] = 1
    no_shrink_mask = np.ones(num_vars) - shrink_mask

    xbeta = design_matrix @ beta
    prior = (
        (beta * no_shrink_mask) ** 2 / (2 * prior_no_shrink_scale**2)
    ).sum() + np.log1p((beta[shrink_index] / prior_scale) ** 2)

    nll = (
        counts * xbeta - (counts + size) * np.logaddexp(xbeta + offset + cnv, np.log(size))
    ).sum(0)

    return prior - nll


def build_design_matrix(
    metadata: pd.DataFrame,
    design_factors: Union[str, List[str]] = "condition",
    ref_level: Optional[List[str]] = None,
    continuous_factors: Optional[List[str]] = None,
    expanded: bool = False,
    intercept: bool = True,
) -> pd.DataFrame:
    """Build design_matrix matrix for DEA.

    Unless specified, the reference factor is chosen alphabetically.

    Parameters
    ----------
    metadata : pandas.DataFrame
        DataFrame containing metadata information.
        Must be indexed by sample barcodes.

    design_factors : str or list
        Name of the columns of metadata to be used as design_matrix variables.
        (default: ``"condition"``).

    ref_level : dict or None
        An optional list of two strings of the form ``["factor", "ref_level"]``
        specifying the factor of interest and the desired reference level, e.g.
        ``["condition", "A"]``. (default: ``None``).

    continuous_factors : list or None
        An optional list of continuous (as opposed to categorical) factors. Any factor
        not in ``continuous_factors`` will be considered categorical (default: ``None``).

    expanded : bool
        If true, use one column per category. Else, use n-1 columns, for each n-level
        categorical factor.
        (default: ``False``).

    intercept : bool
        If true, add an intercept (a column containing only ones). (default: ``True``).

    Returns
    -------
    pandas.DataFrame
        A DataFrame with experiment design information (to split cohorts).
        Indexed by sample barcodes.
    """
    if isinstance(
        design_factors, str
    ):  # if there is a single factor, convert to singleton list
        design_factors = [design_factors]

    for factor in design_factors:
        # Check that each factor has at least 2 levels
        if len(np.unique(metadata[factor])) < 2:
            raise ValueError(
                f"Factors should take at least two values, but {factor} "
                f"takes the single value '{np.unique(metadata[factor])}'."
            )

    # Check that level factors in the design don't contain underscores. If so, convert
    # them to hyphens
    warning_issued = False
    for factor in design_factors:
        if np.any(["_" in value for value in metadata[factor]]):
            if not warning_issued:
                warnings.warn(
                    """Some factor levels in the design contain underscores ('_').
                    They will be converted to hyphens ('-').""",
                    UserWarning,
                    stacklevel=2,
                )
                warning_issued = True
            metadata[factor] = metadata[factor].apply(lambda x: x.replace("_", "-"))

    if continuous_factors is not None:
        categorical_factors = [
            factor for factor in design_factors if factor not in continuous_factors
        ]
    else:
        categorical_factors = design_factors

    # Check that there is at least one categorical factor
    if len(categorical_factors) > 0:
        design_matrix = pd.get_dummies(
            metadata[categorical_factors], drop_first=not expanded
        )

        if ref_level is not None:
            if len(ref_level) != 2:
                raise KeyError("The reference level should contain 2 strings.")
            if ref_level[1] not in metadata[ref_level[0]].values:
                raise KeyError(
                    f"The metadata data should contain a '{ref_level[0]}' column"
                    f" with a '{ref_level[1]}' level."
                )

            # Check that the reference level is not in the matrix (if unexpanded design)
            ref_level_name = "_".join(ref_level)
            if (not expanded) and ref_level_name in design_matrix.columns:
                # Remove the reference level and add one
                factor_cols = [
                    col for col in design_matrix.columns if col.startswith(ref_level[0])
                ]
                missing_level = next(
                    level
                    for level in np.unique(metadata[ref_level[0]])
                    if f"{ref_level[0]}_{level}" not in design_matrix.columns
                )
                design_matrix[f"{ref_level[0]}_{missing_level}"] = 1 - design_matrix[
                    factor_cols
                ].sum(1)
                design_matrix.drop(ref_level_name, axis="columns", inplace=True)

        if not expanded:
            # Add reference level as column name suffix
            for factor in design_factors:
                if ref_level is None or factor != ref_level[0]:
                    # The reference is the unique level that is no longer there
                    ref = next(
                        level
                        for level in np.unique(metadata[factor])
                        if f"{factor}_{level}" not in design_matrix.columns
                    )
                else:
                    # The reference level is given as an argument
                    ref = ref_level[1]
                design_matrix.columns = [
                    f"{col}_vs_{ref}" if col.startswith(factor) else col
                    for col in design_matrix.columns
                ]
    else:
        # There is no categorical factor in the design
        design_matrix = pd.DataFrame(index=metadata.index)

    if intercept:
        design_matrix.insert(0, "intercept", 1)

    # Convert categorical factors one-hot encodings to int
    design_matrix = design_matrix.astype("int")

    # Add continuous factors
    if continuous_factors is not None:
        for factor in continuous_factors:
            # This factor should be numeric
            design_matrix[factor] = pd.to_numeric(metadata[factor])
    return design_matrix

