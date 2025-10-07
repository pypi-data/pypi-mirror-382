# src/huqt_oracle_pysdk/__init__.py
from importlib.metadata import PackageNotFoundError, version

# Public API re-exports
from .websocket import WSClient
from .oracle import OracleClient
from .enums import Side, Tif

# Optional: expose a clean package version
try:
    __version__ = version("huqt_oracle_pysdk")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["OracleClient", "side", "tif", "__version__"]
