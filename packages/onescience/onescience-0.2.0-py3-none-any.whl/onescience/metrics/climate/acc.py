# TODO(Dallas) Introduce Distributed Class for computation.

import torch

from onescience.metrics.climate.reduction import _compute_lat_weights

Tensor = torch.Tensor


def acc(pred: Tensor, target: Tensor, climatology: Tensor, lat: Tensor) -> Tensor:
    """Calculates the Anomaly Correlation Coefficient

    Parameters
    ----------
    pred : Tensor
        [..., H, W] Predicted tensor on a lat/long grid
    target : Tensor
        [..., H, W] Target tensor on a lat/long grid
    climatology : Tensor
        [..., H, W] climatology tensor
    lat : Tensor
        [H] latitude tensor

    Returns
    -------
    Tensor
        ACC values for each field

    Note
    ----
    Reference: https://www.atmos.albany.edu/daes/atmclasses/atm401/spring_2016/ppts_pdfs/ECMWF_ACC_definition.pdf
    """
    if not (pred.ndim > 2):
        raise AssertionError("Expected predictions to have at least two dimensions")
    if not (target.ndim > 2):
        raise AssertionError("Expected predictions to have at least two dimensions")
    if not (climatology.ndim > 2):
        raise AssertionError("Expected predictions to have at least two dimensions")

    # subtract climate means
    pred_hat = pred - climatology
    target_hat = target - climatology

    # Get aggregator
    lat_weight = _compute_lat_weights(lat)
    # Weighted mean
    pred_bar = torch.sum(
        lat_weight[:, None] * pred_hat, dim=(-2, -1), keepdim=True
    ) / torch.sum(
        lat_weight[:, None] * torch.ones_like(pred_hat), dim=(-2, -1), keepdim=True
    )

    target_bar = torch.sum(
        lat_weight[:, None] * target_hat, dim=(-2, -1), keepdim=True
    ) / torch.sum(
        lat_weight[:, None] * torch.ones_like(target_hat), dim=(-2, -1), keepdim=True
    )
    pred_diff = pred_hat - pred_bar
    target_diff = target_hat - target_bar

    p1 = torch.sum(lat_weight[:, None] * pred_diff * target_diff, dim=(-2, -1))
    p2 = torch.sum(lat_weight[:, None] * pred_diff * pred_diff, dim=(-2, -1))
    p3 = torch.sum(lat_weight[:, None] * target_diff * target_diff, dim=(-2, -1))
    m = p1 / torch.sqrt(p2 * p3)
    return m
