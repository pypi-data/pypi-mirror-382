"""Tests for environment detection utilities."""

from unittest.mock import MagicMock, patch

from fiddler_evals.utils.environment import (
    get_ipython,
    is_colab,
    is_ipython,
    is_jupyter,
)


class TestGetIPython:
    """Test cases for get_ipython function."""

    def test_get_ipython_without_ipython(self) -> None:
        """When IPython is not available
        Then it should return None."""
        with patch(
            "fiddler_evals.utils.environment.get_ipython", side_effect=ImportError
        ):
            result = get_ipython()
            assert result is None

    def test_get_ipython_module_not_found(self) -> None:
        """When IPython module is not found
        Then it should return None."""
        with patch(
            "fiddler_evals.utils.environment.get_ipython",
            side_effect=ModuleNotFoundError,
        ):
            result = get_ipython()
            assert result is None


class TestIsJupyter:
    """Test cases for is_jupyter function."""

    def test_is_jupyter_with_kernel(self) -> None:
        """When running in Jupyter with kernel
        Then it should return True."""
        mock_ipython = MagicMock()
        mock_ipython.kernel = MagicMock()

        with patch(
            "fiddler_evals.utils.environment.get_ipython", return_value=mock_ipython
        ):
            result = is_jupyter()
            assert result is True

    def test_is_jupyter_without_kernel(self) -> None:
        """When running in IPython without kernel
        Then it should return False."""
        mock_ipython = MagicMock()
        del mock_ipython.kernel  # Remove kernel attribute

        with patch(
            "fiddler_evals.utils.environment.get_ipython", return_value=mock_ipython
        ):
            result = is_jupyter()
            assert result is False

    def test_is_jupyter_no_ipython(self) -> None:
        """When IPython is not available
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_jupyter()
            assert result is False

    def test_is_jupyter_ipython_none(self) -> None:
        """When get_ipython returns None
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_jupyter()
            assert result is False


class TestIsIPython:
    """Test cases for is_ipython function."""

    def test_is_ipython_with_ipython(self) -> None:
        """When running in IPython environment
        Then it should return True."""
        mock_ipython = MagicMock()

        with patch(
            "fiddler_evals.utils.environment.get_ipython", return_value=mock_ipython
        ):
            result = is_ipython()
            assert result is True

    def test_is_ipython_no_ipython(self) -> None:
        """When IPython is not available
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_ipython()
            assert result is False

    def test_is_ipython_ipython_none(self) -> None:
        """When get_ipython returns None
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_ipython()
            assert result is False


class TestIsColab:
    """Test cases for is_colab function."""

    def test_is_colab_with_google_colab_string(self) -> None:
        """When running in Google Colab
        Then it should return True."""
        mock_ipython = MagicMock()
        mock_ipython.__str__ = MagicMock(return_value="google.colab.kernel")

        with patch(
            "fiddler_evals.utils.environment.get_ipython", return_value=mock_ipython
        ):
            result = is_colab()
            assert result is True

    def test_is_colab_without_google_colab_string(self) -> None:
        """When running in regular IPython
        Then it should return False."""
        mock_ipython = MagicMock()
        mock_ipython.__str__ = MagicMock(return_value="IPython.kernel.zmq")

        with patch(
            "fiddler_evals.utils.environment.get_ipython", return_value=mock_ipython
        ):
            result = is_colab()
            assert result is False

    def test_is_colab_no_ipython(self) -> None:
        """When IPython is not available
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_colab()
            assert result is False

    def test_is_colab_ipython_none(self) -> None:
        """When get_ipython returns None
        Then it should return False."""
        with patch("fiddler_evals.utils.environment.get_ipython", return_value=None):
            result = is_colab()
            assert result is False
