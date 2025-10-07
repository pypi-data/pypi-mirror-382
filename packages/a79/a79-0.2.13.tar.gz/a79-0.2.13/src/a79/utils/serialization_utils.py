"""
Common serialization utilities for A79 models.

This module provides shared serialization functions that can be used
across different model classes to ensure consistent JSON serialization
behavior for complex data types like pandas DataFrames, numpy arrays, etc.
"""

from typing import Any

import numpy as np
import pandas as pd


def serialize_content_recursive(value: Any) -> Any:
    """
    Recursively serialize a value to make it JSON-serializable.

    This function handles:
    - dict/DotDict objects (recursively)
    - lists (recursively)
    - tuples (recursively)
    - sets (converts to list recursively)
    - pandas DataFrames (converts to dict records)
    - pandas Series (converts to list)
    - numpy arrays (converts to list)
    - numpy scalar types (converts to Python primitives)

    Args:
        value: The value to serialize

    Returns:
        A JSON-serializable version of the value
    """
    # Handle pandas objects if pandas is available
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    elif isinstance(value, pd.Series):
        return value.tolist()

    # Handle dict-like objects
    # Note: We check for dict-like behavior instead of importing DotDict
    # to avoid dependencies on common_py from the external package
    elif isinstance(value, dict):
        return {k: serialize_content_recursive(v) for k, v in value.items()}
    elif hasattr(value, "items") and hasattr(value, "__getitem__"):
        # Handle DotDict-like objects that behave like dictionaries
        return {k: serialize_content_recursive(v) for k, v in value.items()}

    # Handle collections
    elif isinstance(value, list):
        return [serialize_content_recursive(v) for v in value]
    elif isinstance(value, tuple):
        return tuple(serialize_content_recursive(v) for v in value)
    elif isinstance(value, set):
        return list(serialize_content_recursive(v) for v in value)

    # Handle numpy objects if numpy is available
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(
        value, (np.int32, np.int64, np.int16, np.int8, np.bool_, np.float32, np.float64)
    ):
        return value.item()

    # Return the value as-is if no special handling is needed
    return value
