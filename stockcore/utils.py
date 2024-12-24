import matplotlib as _mpl
import matplotlib.pyplot as _plt
import torch as _torch

__all__ = [
    'setup_mpl',
    'get_device',
    'is_backend_available'
]

def setup_mpl() -> bool:
    """Set up matplotlib for interactive use in IPython.

    Returns
    -------
    bool
        Whether the current environment is IPython or not.
    """
    is_ipython = 'inline' in _mpl.get_backend()
    if is_ipython:
        from IPython import display

    _plt.ion()

    return is_ipython

def get_device() -> _torch.device:
    """Return the appropriate torch device based on availability.

    Returns
    -------
    torch.device
        The appropriate torch device based on availability.
    """
    return _torch.device(
        "cuda" if _torch.cuda.is_available() else
        "mps" if _torch.backends.mps.is_available() else
        "cpu"
    )

def is_backend_available() -> bool:
    """Check if a GPU backend (MPS or CUDA) is available.

    Returns
    -------
    bool
        Whether a GPU backend (MPS or CUDA) is available or not.
    """
    return _torch.cuda.is_available() or _torch.backends.mps.is_available()