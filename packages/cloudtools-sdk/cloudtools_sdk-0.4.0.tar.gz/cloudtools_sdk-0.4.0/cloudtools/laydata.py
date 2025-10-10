"""LayData integration for CloudTools SDK."""

try:
    from laydata import Data
except ImportError:  # pragma: no cover - exercised via import side effects
    _MISSING_DEP_MSG = (
        "laydata package is required but not installed. "
        "Please install it with: pip install laydata"
    )

    raise ImportError(_MISSING_DEP_MSG)

__all__ = ["Data"]
