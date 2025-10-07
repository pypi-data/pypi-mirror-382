# pyASDReader Examples

This directory contains example scripts demonstrating how to use pyASDReader.

## Available Examples

### 1. basic_usage.py

Demonstrates the fundamental operations with pyASDReader:
- Loading ASD files
- Accessing metadata
- Reading spectral data
- Working with reflectance and derivatives

**Usage:**

```bash
python examples/basic_usage.py
```

**Note:** You need to modify the `file_path` variable in the script to point to your actual `.asd` file.

## Getting Test Data

You can use the sample data included in the `tests/sample_data/` directory for testing:

```python
from pyASDReader import ASDFile

# Example with version 7 sample data
asd = ASDFile("tests/sample_data/v7sample/your_file.asd")
```

## Additional Resources

- [Main README](../README.md) - Full documentation
- [API Documentation](../README.md#usage-examples) - Detailed API usage
- [CHANGELOG](../CHANGELOG.md) - Version history
