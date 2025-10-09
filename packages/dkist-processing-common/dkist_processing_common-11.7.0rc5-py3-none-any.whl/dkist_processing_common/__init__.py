"""Package providing support classes and methods used by all workflow tasks."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

try:
    __version__ = version(distribution_name=__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
