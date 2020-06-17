# package release to pypi

```
python -m venv .venv
source .venv/bin/activate

python3 -m pip install --user --upgrade setuptools wheel twine
sudo rm -R dist
python setup.py sdist bdist_wheel

twine upload dist/*
```
