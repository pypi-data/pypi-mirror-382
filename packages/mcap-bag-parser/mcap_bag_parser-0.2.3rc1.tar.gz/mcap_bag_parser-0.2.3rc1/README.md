# MCAP Bag Parser

Parse MCAP rosbags into pandas dataframes using an adapter around rosx_introspection for speed.

## Installation

```bash
pip install mcap-bag-parser
```

*Note*: The mcap-bag-parser is now a fully self-contained package using `scikit-build-core`, for automatically building/bundling `rosx_introspection` during pip 
  install. Users now get a unified mcap_bag module with both legacy (BagFileParser) and modern (parse_mcap_file) APIs, with scikit-build-core handling C++ compilation and Python extension creation.



## Development

```bash
# Clone with submodules
git clone --recurse-submodules https://gitlab.com/nealtanner/mcap-bag-parser.git
cd mcap-bag-parser

# Install in editable mode (recommended)
pip install -e .

# Run tests
pytest
```

For isolated development alongside other versions:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Rebuilding after C++ changes

```bash
# Update code and submodules
git pull --recurse-submodules  # Or: git pull && git submodule update --init

# Force rebuild (cleans build cache)
pip install --force-reinstall --no-deps -e .

# Or clean everything and rebuild
rm -rf build/ build_python/
pip install -e .
```

## Publishing to PyPI

**Important:** PyPI rejects `linux_x86_64` and `linux_aarch64` wheels. Must use `cibuildwheel` for manylinux tags.

```bash
pip install build twine cibuildwheel
rm -rf dist/ wheelhouse/  # Clean old builds

# Linux - builds manylinux wheels in Docker (required for PyPI)
cibuildwheel --platform linux  # All architectures
# Or specific: --archs x86_64 or --archs aarch64

# macOS - builds universal2 wheels
cibuildwheel --platform macos

# Source distribution
python -m build --sdist

# Upload all
twine upload wheelhouse/*.whl dist/*.tar.gz  # Username: __token__
```

**Supported platforms:**
- Linux: x86_64, aarch64 (manylinux2014)
- macOS: x86_64, arm64 (11.0+)
- Python: >=3.10