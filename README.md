# Summary

processing working time on backlog.

Reference

https://developer.nulab.com/ja/docs/backlog/

## Requirements

- Python 3.7+
- pybacklog
- pipenv install python-dateutil
- pipenv install --dev twine

## Install package

https://pypi.org/project/backlogprocessing/

```
pip install backlogprocessing
```

## Usage

```
from backlogprocessingmodule import *

backlogapiprocessing.run(ConfigFilePath, LoggingConfigFilePath)
```


## For Developer

When you need to upload this package, see package_release.md


### Migrate requirements.txt to Pipfile

https://www.kabuku.co.jp/developers/python-pipenv-graph

```
pipenv install -r requirements.txt
pipenv graph
```
