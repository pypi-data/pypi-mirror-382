from .client import GraphonClient

try:
    # Python 3.8+
    from importlib.metadata import PackageNotFoundError, version
except Exception:  # pragma: no cover
    # Fallback for environments with backport
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

try:
    __version__ = version("graphon-client")
except PackageNotFoundError:
    # Package not installed (e.g., running from source). Keep a sensible fallback.
    __version__ = "0.0.0"

__all__ = ["GraphonClient", "__version__"]


