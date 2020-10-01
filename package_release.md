# package release to pypi

<!-- 

modify setup function in setup.py

```
version [new version]
```

upload command

```
python -m venv .venv
source .venv/bin/activate

python3 -m pip install --user --upgrade setuptools wheel twine
sudo rm -R dist
python setup.py sdist bdist_wheel

twine upload dist/*
``` -->

```
pipenv shell
pipenv install --dev twine
python3 setup.py sdist --formats=zip
twine upload dist/*
```
