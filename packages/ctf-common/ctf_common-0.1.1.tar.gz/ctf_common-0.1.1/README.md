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
   python -m build
    twine upload dist/*
```


### 安装构建工具
pip install build twine

### 构建源码包和wheel包
python -m build

