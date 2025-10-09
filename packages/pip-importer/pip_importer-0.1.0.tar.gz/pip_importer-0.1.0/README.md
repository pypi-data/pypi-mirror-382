# Welcome

This is a small Python utility which can import a package, or pip install first if the package does not exist.


#  Installation

```bash
pip install pip-importer
```

# Usage

```python
import pip_importer

# This is same as `import pytest`
# Or `pip install pytest` then `import pytest` if pytest is not installed
pip_importer.pip_import("pytest")
```
