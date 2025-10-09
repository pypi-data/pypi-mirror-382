## New:
import logging
from typing import List, Dict, Any, Union, Set
import numpy as np

logger = logging.getLogger(__name__)


def _get_inner_type(item: Any) -> str:
    """Recursively determines the type, handling lists and NumPy arrays."""
    if isinstance(item, (list, tuple, np.ndarray)):
        # If it's empty, we can't determine the inner type right now.
        # Use specific check for emptiness to avoid ValueError with multi-element numpy arrays.
        is_empty = (
            (isinstance(item, np.ndarray) and item.size == 0) or
            (not isinstance(item, np.ndarray) and not item)
        )
        if is_empty:
            return f"{type(item).__name__}[Unknown]"

        # Check the types of the first few elements (or all if small)
        sample_size = min(len(item), 5)
        inner_types = set()
        for element in item[:sample_size]:
            inner_types.add(_get_inner_type(element))

        # Simplify the representation of inner types
        if len(inner_types) == 1:
            inner_type_str = list(inner_types)[0]
        elif len(inner_types) > 1:
            inner_type_str = "Mixed"
        else:
            inner_type_str = "Unknown"

        return f"{type(item).__name__}[{inner_type_str}]"

    elif isinstance(item, np.generic):
        # Handle NumPy scalar types
        return f"numpy.{item.dtype.name}"

    # Simple Python type
    return type(item).__name__


def log_record_types(rows: List[Dict[str, Any]], log_file_path: str = "record_types_plankton.log"):
    """
    Analyzes a list of records (dictionaries) and logs the observed types for each column
    to a specified log file. Handles nested types (list, numpy.ndarray).
    """
    # Temporarily set up a file handler for this specific logging task
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setFormatter(logging.Formatter('%(message)s'))

    # Use a dedicated logger for this output to avoid mixing with regular application logs
    type_logger = logging.getLogger("RecordTypeLogger")
    type_logger.setLevel(logging.INFO)
    type_logger.addHandler(file_handler)
    type_logger.propagate = False  # Don't pass to root logger

    column_types: Dict[str, Set[str]] = {}

    type_logger.info("--- Starting Record Type Analysis ---")

    if not rows:
        type_logger.info("Input list of rows is empty.")
        type_logger.removeHandler(file_handler)
        file_handler.close()
        return

    # Pass 1: Collect all unique types observed for each column
    for i, row in enumerate(rows):
        for col, value in row.items():
            if col not in column_types:
                column_types[col] = set()

            # Use the helper function to get the full type string
            type_str = _get_inner_type(value)

            # Special handling for None (Missing values)
            if value is None:
                type_str = "NoneType (Missing)"

            column_types[col].add(type_str)

    # Pass 2: Log the final result for each column
    sorted_cols = sorted(column_types.keys())
    for col in sorted_cols:
        types_str = ", ".join(sorted(column_types[col]))
        log_message = f"Column '{col}' observed types: {types_str}"
        type_logger.info(log_message)

    type_logger.info("--- Record Type Analysis Complete ---")

    # Clean up the temporary handler
    type_logger.removeHandler(file_handler)
    file_handler.close()

##