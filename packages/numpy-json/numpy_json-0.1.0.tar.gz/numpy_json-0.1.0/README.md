# numpy-json

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A robust JSON encoder for NumPy arrays and extended Python data types. No more writing custom serialization wrappers — just drop in `NumpyJSONEncoder` and go.

## Features

**numpy-json** seamlessly handles:

- **NumPy arrays** → JSON lists
- **NumPy scalars** (int, float, bool) → native JSON types
- **NumPy datetime64/timedelta64** → ISO 8601 strings
- **Python datetime/date/time** → ISO 8601 strings
- **UUID** → string representation
- **Decimal** → float (default) or string (configurable)
- **set/tuple** → JSON lists
- **bytes/bytearray** → base64 encoded strings (configurable)
- **pathlib.Path** → string paths
- **pandas types** (optional, no hard dependency) → appropriate JSON types

## Installation

```bash
pip install numpy-json
```

Or install from source:

```bash
git clone https://github.com/featrix/numpy-json.git
cd numpy-json
pip install -e .
```

## Quick Start

```python
import json
import numpy as np
from numpy_json import NumpyJSONEncoder

# Your data with NumPy arrays
data = {
    "array": np.array([1, 2, 3, 4, 5]),
    "matrix": np.array([[1, 2], [3, 4]]),
    "scalar": np.float64(3.14159),
    "date": np.datetime64('2025-01-15'),
}

# Encode to JSON - it just works!
json_str = json.dumps(data, cls=NumpyJSONEncoder)
print(json_str)
```

**Output:**
```json
{
  "array": [1, 2, 3, 4, 5],
  "matrix": [[1, 2], [3, 4]],
  "scalar": 3.14159,
  "date": "2025-01-15"
}
```

## Usage

### Basic Usage

Simply pass `NumpyJSONEncoder` as the `cls` parameter to `json.dumps()`:

```python
import json
from numpy_json import NumpyJSONEncoder

json_str = json.dumps(your_data, cls=NumpyJSONEncoder)
```

### Configuration Options

The encoder provides class-level configuration:

#### Decimal Handling

```python
from numpy_json import NumpyJSONEncoder
import decimal

# Default: convert Decimal to float (lossy for very precise decimals)
data = {"price": decimal.Decimal("19.99")}
json.dumps(data, cls=NumpyJSONEncoder)  # → {"price": 19.99}

# Alternative: preserve as string
NumpyJSONEncoder.DECIMAL_AS_STR = True
json.dumps(data, cls=NumpyJSONEncoder)  # → {"price": "19.99"}
```

#### Binary Data Handling

```python
from numpy_json import NumpyJSONEncoder

data = {"binary": b"hello world"}

# Default: base64 encoding
json.dumps(data, cls=NumpyJSONEncoder)  
# → {"binary": "aGVsbG8gd29ybGQ="}

# Alternative: emit as integer list
NumpyJSONEncoder.BASE64_BYTES = False
json.dumps(data, cls=NumpyJSONEncoder)
# → {"binary": [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]}
```

### Handling NaN and Infinity

By default, Python's `json` module allows `NaN` and `Infinity` values (which are not valid in RFC 8259 JSON). If you need strict JSON compliance:

```python
import json
import numpy as np
from numpy_json import NumpyJSONEncoder, sanitize_nans

data = {
    "valid": np.array([1.0, 2.0, 3.0]),
    "invalid": np.array([1.0, np.nan, np.inf, -np.inf]),
}

# Clean the data first
clean_data = sanitize_nans(data)
# NaN/Inf values are replaced with None

# Then encode with allow_nan=False for strict JSON
json_str = json.dumps(clean_data, cls=NumpyJSONEncoder, allow_nan=False)
```

**Result:**
```json
{
  "valid": [1.0, 2.0, 3.0],
  "invalid": [1.0, null, null, null]
}
```

### Advanced Example

```python
import json
import numpy as np
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from numpy_json import NumpyJSONEncoder

complex_data = {
    "id": uuid4(),
    "timestamp": datetime.now(),
    "measurements": np.array([1.5, 2.3, 3.7, 4.1]),
    "matrix": np.random.rand(3, 3),
    "metadata": {
        "path": Path("/tmp/data.csv"),
        "tags": {"ml", "experiment", "2025"},
        "coordinates": (40.7128, -74.0060),
    },
    "config": {
        "enabled": np.bool_(True),
        "threshold": np.float32(0.85),
        "max_items": np.int64(1000),
    }
}

json_str = json.dumps(complex_data, cls=NumpyJSONEncoder, indent=2)
print(json_str)
```

## API Reference

### `NumpyJSONEncoder`

**Class Attributes:**
- `DECIMAL_AS_STR` (bool): If `True`, encode `Decimal` as string. Default: `False`
- `BASE64_BYTES` (bool): If `True`, encode bytes as base64. Default: `True`

**Methods:**
- `default(obj)`: Override method that handles type conversion

### `sanitize_nans(obj)`

Recursively replace `NaN`, `Inf`, and `-Inf` values with `None`.

**Parameters:**
- `obj`: Any Python object (dict, list, NumPy array, etc.)

**Returns:**
- Object with all NaN/Inf values replaced with `None`

## Type Conversion Table

| Python/NumPy Type | JSON Output | Notes |
|-------------------|-------------|-------|
| `np.ndarray` | Array | Recursive conversion via `.tolist()` |
| `np.int*` | Number | All NumPy integer types |
| `np.float*` | Number | All NumPy float types |
| `np.bool_` | Boolean | NumPy boolean |
| `np.datetime64` | String | ISO 8601 format |
| `np.timedelta64` | String | Duration string |
| `datetime`/`date`/`time` | String | ISO 8601 format |
| `uuid.UUID` | String | Standard UUID string |
| `decimal.Decimal` | Number or String | Configurable via `DECIMAL_AS_STR` |
| `set`/`tuple` | Array | Converted to list |
| `bytes`/`bytearray` | String or Array | Configurable via `BASE64_BYTES` |
| `pathlib.Path` | String | String representation |
| pandas types | String or `null` | Optional support, no hard dependency |

## Requirements

- Python 3.8+
- NumPy

## Development

### Setup

```bash
git clone https://github.com/featrix/numpy-json.git
cd numpy-json
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

```bash
black numpy_json/
flake8 numpy_json/
mypy numpy_json/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright

Copyright (c) 2025 Featrix, Inc.

## Acknowledgments

- Built to solve real-world data serialization challenges in scientific computing and machine learning workflows
- Inspired by the need for seamless NumPy integration with JSON APIs

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/featrix/numpy-json).
