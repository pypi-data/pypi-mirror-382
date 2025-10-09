from typing import Tuple
import warnings

import torch
from torch import Tensor
from torch import linalg


def _check_tall_matrix(A: Tensor) -> None:
    """Raises an exception if a matrix is not a tall matrix."""
    
    if A.ndim != 2:
        msg = "Input tensor must be two-dimensional."
        raise Exception(msg)
    
    n, r = A.shape
    if r > n:
        msg = (
            "The number of rows of the input matrix must be greater "
            f"than or equal to the number of columns ({n} vs {r})."
        )
        raise Exception(msg)
    
    return


def _get_lu_pivots(A: Tensor) -> Tensor:
    # Note: this seems to give the same results at the DEIM 
    # implementation below.

    n = A.shape[0]
    inds = torch.arange(n)

    pivots: Tensor = linalg.lu_factor_ex(A)[1] - 1
    for i, p in enumerate(pivots):
        inds[[i, p.item()]] = inds[[p.item(), i]]

    return inds


def deim(U: Tensor) -> Tuple[Tensor, Tensor]:
    """Computes a submatrix of a matrix of left singular vectors using
    the discrete empirical interpolation method (DEIM).
    
    Parameters
    ----------
    U: 
        An n * r matrix of left singular vectors, where n >= r. The 
        vectors should be in order of decreasing singular value.
        
    Returns
    -------
    indices:
        The indices of the submatrix found using the DEIM.
    B: 
        The product of U and the inverse of the submatrix found using 
        the DEIM.
    
    References
    ----------
    Chaturantabut, S and Sorensen, DC (2010). Nonlinear model reduction 
    via discrete empirical interpolation.

    """

    _check_tall_matrix(U)
    n, r = U.shape 

    inds = torch.zeros(r, dtype=torch.int)
    P = torch.zeros((n, r))

    inds[0] = U[:, 0].abs().argmax()
    P[inds[0], 0] = 1.0

    for i in range(1, r):

        P_i = P[:, :i]
        U_i = U[:, :i]

        c: Tensor = linalg.solve(P_i.T @ U_i, P_i.T @ U[:, i])
        r = U[:, i] - U[:, :i] @ c
        inds[i] = r.abs().argmax()
        P[inds[i], i] = 1.0

    B = linalg.solve(U[inds], U, left=False)
    return inds, B


def maxvol(
    H: Tensor, 
    tol: float = 1e-2,
    max_iter: int = 200
) -> Tuple[Tensor, Tensor]:
    """Returns a dominant r*r submatrix within an n*r matrix.
    
    Parameters
    ----------
    H:
        n*r matrix, where n > r.
    tol:
        Convergence tolerance. The algorithm is considered converged if
        the absolute value of the largest element in H^{-1} @ B (where 
        B is the submatrix identified) is no greater than 1 + tol.
    max_iter:
        The maximum number of iterations to carry out.

    Returns
    -------
    inds:
        The row indices of the dominant submatrix. 
    B:
        The product of H and the inverse of the submatrix.

    References
    ----------
    Goreinov, SA, et al. (2010). How to find a good submatrix.

    """

    _check_tall_matrix(H)
    _, r = H.shape
    inds = _get_lu_pivots(H)[:r]

    if (rank := linalg.matrix_rank(H[inds])) < r:
        msg = f"Initial submatrix is singular (rank {rank} < {r})."
        raise Exception(msg)

    B: Tensor = linalg.solve(H[inds].T, H.T).T

    for _ in range(max_iter):

        ij_max = B.abs().argmax(dim=None)
        i, j = torch.unravel_index(ij_max, B.shape)
        i_old = inds[j]

        if B[i, j].abs() < 1.0 + tol:
            # print(torch.max(B @ linalg.inv(B[inds[:r]])))
            return inds, B

        B -= torch.outer(B[:, j], (B[i, :] - B[i_old, :]) / B[i, j])
        inds[j] = i

    msg = f"maxvol failed to converge in {max_iter} iterations."
    warnings.warn(msg)
    return inds, B