"""
This module contains some utils functions.
"""

import os
import random
import numpy as np
from typing import List, Optional
import logging
import torch


def get_logger():
    """
    Get a logger instance.
    """

    logger = logging.getLogger("quantselect")
    if logger.handlers:
        logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def create_mask_based_on_percentile(matrix, percentile):
    """
    Filter matrix based on percentile.

    Parameters
    ----------
        matrix : torch.tensor
            Data for filtering.

        percentile : float
            Percentile for filtering.

    Returns
    -------
        matrix : torch.tensor
            Filtered matrix.

    """

    percentile = np.nanpercentile(matrix, percentile)
    mask = matrix >= percentile

    return mask


def extract_feature_level_data(data, feature_idx):
    """
    Extract a specific feature from a list
    of a 3D tensor of shape (n_fragments, n_features, n_samples).

    Parameters
    ----------
    data : list
        List of 3D tensors of shape
        (n_fragments, n_features, n_samples).

    feature_idx : int
        Index of the feature to extract.

    Returns
    -------
    list
        List of 2D array of shape
        (n_fragments, n_samples).
    """
    return [np.array(matrix[:, :, feature_idx]) for matrix in data]


def filter_list_by_mask(data, mask):
    """
    Filter a list of datasets by a mask.
    """
    return [data[i] for i in range(len(data)) if mask[i]]


# def repeater(data, function, instance_method, **kwargs):
#     if instance_method:
#         return [getattr(subset, function)(**kwargs) for subset in data]
#     else:
#         return [function(subset, **kwargs) for subset in data]


def repeater(data, function, instance_method, unpack_input=False, **kwargs):
    """
    This function applies a given function repeatedly to
    each element in the input data.

    Parameters:
    -------
    data: iterable
        An iterable containing the data to be processed. Each
        element can be a single item or an iterable (list or tuple)
        if multiple arguments need to be passed to the function.

    function: callable or str
        The function to be applied. If instance_method is True, this should be a string
        representing the method name. Otherwise, it should be a callable object.

    instance_method: bool
        If True, the function is treated as a method of the first element in each subset.
        If False, the function is treated as a standalone function.

    unpack_input: bool
        If True, each element in the data is unpacked and passed as
        separate arguments to the function.
        If False, each element is passed as a single

    **kwargs: dict
        Additional keyword arguments to be passed to the function.

    Returns:
    -------
    results: list
        A list containing the results of applying the function to
        each element in the input data.
    """
    results = []

    if not isinstance(data, (list, tuple)):
        data = [data]

    for subset in data:
        if instance_method:
            if unpack_input and isinstance(subset, (list, tuple)):
                result = getattr(subset[0], function)(*subset[1:], **kwargs)
            else:
                result = getattr(subset, function)(**kwargs)
        else:
            if unpack_input and isinstance(subset, (list, tuple)):
                result = function(*subset, **kwargs)
            else:
                result = function(subset, **kwargs)
        results.append(result)
    return results[0] if len(results) == 1 else results


def set_global_determinism(
    seed: int = 42,
    pytorch_deterministic: bool = True,
    cuda_deterministic: bool = True,
    python_hash_seed: bool = True,
    torch_num_threads: Optional[int] = 1,
):
    """
    Set seeds and flags for deterministic behavior across numpy, Python, and PyTorch.

    Parameters
    ----------
    seed : int
        Seed value to set for RNGs.
    pytorch_deterministic : bool
        If True, enforce deterministic algorithms in PyTorch where possible.
    cuda_deterministic : bool
        If True and CUDA is available, set CUDA-specific determinism flags and env.
    python_hash_seed : bool
        If True, set PYTHONHASHSEED for deterministic hashing.
    torch_num_threads : Optional[int]
        If provided, set intra/inter-op thread counts for PyTorch to stabilize results.
    """

    # Python and NumPy
    if python_hash_seed:
        os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    # PyTorch CPU/GPU
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    if pytorch_deterministic:
        try:
            torch.use_deterministic_algorithms(True)
        except (RuntimeError, AttributeError):
            pass

    if torch_num_threads is not None:
        try:
            torch.set_num_threads(torch_num_threads)
            torch.set_num_interop_threads(max(1, torch_num_threads))
        except (RuntimeError, AttributeError):
            pass

    # cuDNN / CUDA flags
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = False
        if cuda_deterministic:
            torch.backends.cudnn.deterministic = True
            # Required by some CUDA backends for full determinism
            # Values: ':16:8' or ':4096:8' depending on device; use one commonly supported
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")


def count_valid_values(data: np.array) -> int:
    """
    Count the number of valid values in a dataset.

    Parameters:
    -------
    data: np.array
        The dataset to be processed.

    Returns:
    -------
    no_valid_values: int
        The number of valid values in the dataset.
    """

    no_valid_values = np.isfinite(data).flatten().sum()
    return no_valid_values


def rank_by_no_valid_vals(data: List[np.array]) -> np.array:
    """
    Rank the datasets based on the number of valid values.

    Parameters:
    -------
    data: np.array
        The dataset to be processed.

    Returns:
    -------
    ranks: np.array
        The ranks of the datasets based on the number of valid values.
    """
    no_valid_vals = np.array([count_valid_values(i) for i in data])

    ranks = no_valid_vals.argsort()[::-1]

    return ranks


def rank(data: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Rank values by size along specified axis.
    Larger values get lower ranks.

    Parameters
    ----------
    data : np.ndarray
        Input array
    axis : int, optional
        Axis along which to rank, by default 0

    Returns
    -------
    np.ndarray
        Array of same shape as input, where each value is replaced by its rank
    """
    data = np.nan_to_num(data, 0)
    ranks = data.shape[axis] - np.argsort(np.argsort(data, axis=axis), axis=axis)
    return ranks
