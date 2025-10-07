# This file is part of Minnt <http://github.com/foxik/minnt/>.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import random

import numpy as np
import torch


def startup(
    seed: int | None = None,
    threads: int | None = None,
    *,
    forkserver_instead_of_fork: bool = True,
    allow_tf32: bool = True,
    expandable_segments: bool | None = True,
) -> None:
    """Initialize the environment.

    - Set the random seed if given.
    - Set the number of threads if given.
    - Use `forkserver` instead of `fork` multiprocessing start method unless disallowed.
    - Allow using TF32 for matrix multiplication unless disallowed.
    - Enable expandable segments in the CUDA memory allocator unless disallowed.

    Parameters:
      seed: If not `None`, set the Python, Numpy, and PyTorch random seeds to this value.
      threads: If not `None` of 0, set the number of threads to this value.
        Otherwise, use as many threads as cores.
      forkserver_instead_of_fork: If `True`, use `forkserver` instead of `fork` as the
        default start multiprocessing method. This will be the default one in Python 3.14.
      allow_tf32: If `False`, disable TF32 for matrix multiplication even when available.
      expandable_segments: If `True`, enable expandable segments in the CUDA memory allocator;
        if `False`, disable them; if `None`, do not change the current setting.

    **Environment variables:** The following environment variables can be used
    to override the method parameters:

    - `MINNT_START_METHOD`: If set to `fork` or `forkserver`, uses the specified method as
      the multiprocessing start method.
    - `MINNT_ALLOW_TF32`: If set to `0` or `1`, overrides the `allow_tf32` parameter.
    - `MINTT_EXPANDABLE_SEGMENTS`: If set to `0` or `1`, overrides the `expandable_segments` parameter.
    """

    # Set random seed if not None.
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    # Set number of threads if > 0; otherwise, use as many threads as cores.
    if threads is not None and threads > 0:
        if torch.get_num_threads() != threads:
            torch.set_num_threads(threads)
        if torch.get_num_interop_threads() != threads:
            torch.set_num_interop_threads(threads)

    # If instructed, use `forkserver` instead of `fork` (which will be the default in Python 3.14).
    if "fork" in torch.multiprocessing.get_all_start_methods():
        if os.environ.get("MINNT_START_METHOD") == "fork":
            if torch.multiprocessing.get_start_method(allow_none=True) != "fork":
                torch.multiprocessing.set_start_method("fork")
        elif forkserver_instead_of_fork or os.environ.get("MINNT_START_METHOD") == "forkserver":
            if torch.multiprocessing.get_start_method(allow_none=True) != "forkserver":
                torch.multiprocessing.set_start_method("forkserver")

    # Allow TF32 for matrix multiplication if available, unless instructed otherwise.
    if os.environ.get("MINNT_ALLOW_TF32") in ["0", "1"]:
        allow_tf32 = os.environ.get("MINNT_ALLOW_TF32") == "1"
    torch.backends.cuda.matmul.allow_tf32 = allow_tf32

    # On NVIDIA GPUs, allow or disallow expandable segments in the CUDA memory allocator if requested.
    if os.environ.get("MINNT_EXPANDABLE_SEGMENTS") in ["0", "1"]:
        expandable_segments = os.environ.get("MINNT_EXPANDABLE_SEGMENTS") == "1"
    if expandable_segments is not None:
        expandable_segments = bool(expandable_segments)
        if f"expandable_segments:{str(not expandable_segments)}" not in os.environ.get("PYTORCH_CUDA_ALLOC_CONF", ""):
            if torch.cuda.is_available() and torch.version.cuda:
                torch.cuda.memory._set_allocator_settings(f"expandable_segments:{str(expandable_segments)}")
