## Environment Requirements

- Python 3.7 and higher
- pip

## Installation
create and activate a virtual environment:
```
python -m venv .venv
Windows:  .venv\Scripts\activate
macOS/Linux: source ./.venv/bin/activate
```
```bash
 pip install -r requirements.txt
 python -m pip install --upgrade pip
 pip install --upgrade setuptools
```

## Install Requirements:
```
 pip install -r requirements.txt
```

## Build lib
```
    pip install build
    python -m build
    pip install .
    pip install build twine
    twine upload dist/*
```

