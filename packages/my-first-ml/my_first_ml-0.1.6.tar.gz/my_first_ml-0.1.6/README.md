# my-first-ml

A test package for ML explanation utilities.

## Installation

```bash
pip install my-first-ml
```

## Quick Start

```python
import mtme

# Print a simple greeting
mtme.hello()  # Output: Hello!
```

## Usage

```python
import mtme

# Call the hello function
mtme.hello()
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/my-first-ml.git
cd my-first-ml
pip install -e .
```

### Building the Package

```bash
pip install build
python -m build
```

### Publishing to PyPI

```bash
pip install twine
twine upload dist/*
```