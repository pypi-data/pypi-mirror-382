"""
Functional module

Contains the functional implementation of masked normalization.
"""

from __future__ import annotations
from typing import Optional

from torch import Tensor, permute

from .validation import validate_masked_norm
from .validation import validate_affine_masked_norm
from .util import unsqueeze_as


def masked_norm(
    inpt: Tensor,
    mask: Optional[Tensor] = None,
) -> Tensor:
    """
    Masked normalization procedure.

    Normalizes elements of the input specified by a mask. The normalization is
    performed along the last axis. If a selection of samples yields null
    variance, the normalization over those elements is ignored, and the values
    are passed along unaltered.
    """

    validate_masked_norm(inpt, mask)

    *_, n = list(inpt.shape)

    if n > 1:
        var = inpt.var(dim=-1, keepdim=True)
    else:
        return inpt

    mean = inpt.mean(dim=-1, keepdim=True)

    var_mask = (var != 0.0).squeeze(-1)
    if mask is None:
        mask = var_mask
    else:
        mask = unsqueeze_as(mask, var_mask)
        mask |= var_mask

    norm = inpt[mask] - mean[mask]
    norm = norm / var[mask].sqrt()

    clone = inpt.clone()
    clone[mask] = norm

    return clone


def affine_masked_norm(
    inpt: Tensor,
    mask: Optional[Tensor],
    weight: Tensor,
    bias: Optional[Tensor],
) -> Tensor:
    """
    Affine masked normalization procedure.

    Normalizes elements of the input specified by a mask. The normalization is
    performed along the last axis. If a selection of samples yields null
    variance, the normalization over those elements is ignored, and the values
    are passed along unaltered. After normalization an affine transformation
    is applied along the normalized axis.
    """

    validate_affine_masked_norm(inpt, mask, weight, bias)

    inpt = masked_norm(inpt, mask)

    inpt = weight[..., None] * inpt

    if bias is not None:
        inpt = inpt + bias[..., None]

    return inpt


def batched_masked_norm(inpt: Tensor, mask: Optional[Tensor]) -> Tensor:
    """
    Batched masked normalization procedure.

    Normalizes elements of the input specified by a mask. The normalization is
    performed along the first axis. If a selection of samples yields null
    variance, the normalization over those elements is ignored, and the values
    are passed along unaltered. Standard masked normalization is performed
    along the last axis, which is usually populated with features. Batched
    masked normalization reverses this order by normalizing along the first
    axis.
    """

    shape = inpt.shape
    n = len(shape)

    perm = list(range(1, n)) + [0]
    inpt = permute(inpt, perm)

    inpt = masked_norm(inpt, mask)

    inv_perm = [n - 1] + list(range(0, n - 1))
    inpt = permute(inpt, inv_perm)

    return inpt


def batched_affine_masked_norm(
    inpt: Tensor,
    mask: Optional[Tensor],
    weight: Tensor,
    bias: Optional[Tensor],
) -> Tensor:
    """
    Batched affine masked normalization procedure.

    Normalizes elements of the input specified by a mask. The normalization is
    performed along the first axis. If a selection of samples yields null
    variance, the normalization over those elements is ignored, and the values
    are passed along unaltered. After normalization an affine transformation
    is applied along the normalized axis. Standard masked normalization is
    performed along the last axis, which is usually populated with features.
    Batched masked normalization reverses this order by normalizing along the
    first axis.
    """

    shape = inpt.shape
    n = len(shape)

    perm = list(range(1, n)) + [0]
    inpt = permute(inpt, perm)

    validate_affine_masked_norm(inpt, mask, weight, bias)

    inpt = masked_norm(inpt, mask)

    inpt = weight[..., None] * inpt

    if bias is not None:
        inpt = inpt + bias[..., None]

    inv_perm = [n - 1] + list(range(0, n - 1))
    inpt = permute(inpt, inv_perm)

    return inpt
