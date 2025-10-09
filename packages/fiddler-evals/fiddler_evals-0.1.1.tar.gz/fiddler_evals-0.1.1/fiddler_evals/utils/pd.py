from importlib.util import find_spec


def validate_pandas_installation() -> None:
    """Validate if pandas is installed."""
    if not find_spec("pandas"):
        raise ImportError(
            "Pandas library is required for this method, install it with `pip install pandas`."
        )
