from importlib import metadata as importlib_metadata

from .convert_utils import convert
from .merge_utils import merge_dbs


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:
        return "unknown"


version: str = get_version()
