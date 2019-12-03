# package release to pypi

```
python -m venv .venv
source .venv/bin/activate

python setup.py sdist bdist_wheel

twine upload dist/*
```
