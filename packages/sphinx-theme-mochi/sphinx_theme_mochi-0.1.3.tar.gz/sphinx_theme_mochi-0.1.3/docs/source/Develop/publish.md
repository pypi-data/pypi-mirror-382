# Publish

This project uses **flit** for deployment. Install it first.

create ~/.pypirc. (If you do not use testpypi, this phase may be skipped)

```sh
# .pypirc
[distutils]
index-servers = 
  pypi
  testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = username

[testpypi]
repository = https://test.pypi.org/legacy/
username = username
```

check `pyproject.toml`

```toml
[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "sphinx_theme_mochi"
...
```

update `__init__.py` to change version and description.

```
#__init__.py

"""package description"""
__version__ = "0.1.0"
```

commit all local changes, then execute publish command with flit. make sure to ignore `/dist` if not yet done.

```sh
flit publish

flit publish --repository testpypi # optional
flit build # build test
```