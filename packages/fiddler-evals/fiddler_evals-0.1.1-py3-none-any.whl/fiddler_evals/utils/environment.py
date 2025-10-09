from __future__ import annotations

from typing import Any


def get_ipython() -> Any:
    """Get the IPython instance."""
    try:
        import IPython
    except (ImportError, ModuleNotFoundError):
        return None

    return IPython.get_ipython()


def is_jupyter() -> bool:
    """
    Check if the python code is executing in Jupyter (notebook, lab, or console).
    """
    ipython = get_ipython()
    if not ipython:
        return False

    return hasattr(ipython, "kernel")


def is_ipython() -> bool:
    """
    Check if the python code is executing in IPython environment.
    """
    ipython = get_ipython()
    if not ipython:
        return False

    return ipython is not None


def is_colab() -> bool:
    """
    Check if the python code is executing in Google Colab.
    """
    ipython = get_ipython()
    if not ipython:
        return False

    return "google.colab" in str(ipython)
