"""
numpy-json: JSON encoder for NumPy arrays and Python data types

Copyright (c) 2025 Featrix, Inc.
Licensed under the MIT License - see LICENSE file for details.
"""

import json
import math
import base64
import uuid
import decimal
from datetime import date, datetime, time
from pathlib import Path

import numpy as np

__version__ = "0.1.0"
__all__ = ["NumpyJSONEncoder", "sanitize_nans"]


class NumpyJSONEncoder(json.JSONEncoder):
    """
    Drop-in JSON encoder for use with json.dumps(..., cls=NumpyJSONEncoder).

    Handles:
      - NumPy arrays -> lists
      - NumPy scalars (int/float/bool) -> native
      - np.datetime64 / np.timedelta64 -> ISO 8601 strings
      - datetime/date/time -> ISO 8601 strings
      - UUID -> str
      - Decimal -> float (lossy) or str (set DECIMAL_AS_STR=True)
      - set/tuple -> list
      - bytes/bytearray -> base64 str
      - pathlib.Path -> str

    Notes:
      - If you want strict RFC 8259 JSON (no NaN/Infinity), call
        json.dumps(..., allow_nan=False) *after* pre-cleaning your data;
        see `sanitize_nans()` below.
    """

    DECIMAL_AS_STR = False  # set True if you want exact Decimal strings
    BASE64_BYTES = True     # set False to emit bytes as list[int]

    def default(self, obj):  # noqa: C901
        # --- NumPy arrays & scalars ---
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            # leave as float; caller can use allow_nan=False + sanitize if needed
            return v
        if isinstance(obj, (np.bool_,)):
            return bool(obj)

        # Datetime-like from NumPy
        if isinstance(obj, np.datetime64):
            # to ISO (UTC-like string without timezone info)
            return np.datetime_as_string(obj, unit='auto')
        if isinstance(obj, np.timedelta64):
            # ISO-ish duration string
            return str(obj)

        # --- Standard library types ---
        if isinstance(obj, (datetime, date, time)):
            # Use ISO 8601; strip microseconds on time if desired
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)

        if isinstance(obj, uuid.UUID):
            return str(obj)

        if isinstance(obj, decimal.Decimal):
            return str(obj) if self.DECIMAL_AS_STR else float(obj)

        if isinstance(obj, (set, tuple)):
            return list(obj)

        if isinstance(obj, (bytes, bytearray)):
            if self.BASE64_BYTES:
                return base64.b64encode(obj).decode('ascii')
            else:
                return list(obj)

        if isinstance(obj, Path):
            return str(obj)

        # --- Optional: pandas without hard dep ---
        pd_ts = getattr(obj, "__class__", None).__class__ if obj is None else obj.__class__
        name = getattr(pd_ts, "__name__", "")
        module = getattr(pd_ts, "__module__", "")
        if "pandas" in module:
            # pandas.Timestamp / pandas.Timedelta / pandas.NaT / pandas NA scalars
            s = str(obj)
            # For NA-like, emit None
            if s in ("NaT", "NaN") or s.lower() == "<na>":
                return None
            return s

        # Fallback to super
        return super().default(obj)


def sanitize_nans(obj):
    """
    Recursively replace NaN/Inf/-Inf floats (including NumPy scalars) with None,
    so you can run json.dumps(..., allow_nan=False) for RFC-compliant JSON.
    
    Args:
        obj: Any Python object (dict, list, numpy array, etc.)
        
    Returns:
        Object with all NaN/Inf values replaced with None
    """
    if isinstance(obj, dict):
        return {str(k): sanitize_nans(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_nans(v) for v in obj]
    if isinstance(obj, (np.floating,)):
        f = float(obj)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, np.ndarray):
        return sanitize_nans(obj.tolist())
    return obj

