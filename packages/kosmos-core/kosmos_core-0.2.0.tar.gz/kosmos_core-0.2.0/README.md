# Kosmos

Koordinations-, Optimierungs- und Simulations-Software für Modulare Quanten-Systeme in 6G Netzwerken

Make sure that you have Python version >=3.13

## Installation

### Install from PyPI (when published)

```sh
pip install kosmos-core
```

## Development Setup

### Create virtual environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
```

### Install dependencies

```sh
pip install -r requirements.txt
```

### Run (usually not necessary for a package, since only functions get imported)

```sh
python -m kosmos.main
```

### Run tests

```sh
pytest -v
```

### Get test coverage

```sh
python -m pytest --cov=kosmos --cov-report=term-missing -q
```

or as HTML

```sh
python -m pytest --cov=kosmos --cov-report=html -q
```

### Run lint

```sh
ruff check .
```

### Run format

```sh
ruff format .
```

## Building and Publishing

### Build the package

```sh
python -m build
```

### Publish to PyPI

```sh
pip install twine
twine upload dist/*
```
