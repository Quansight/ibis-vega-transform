# jupyterlab-omnisci

Connect to OmniSci, query their databases, and render the OmniSci-flavored Vega specification,
all within JupyterLab.

[![](https://img.shields.io/pypi/v/jupyterlab-omnisci.svg)](https://pypi.python.org/pypi/jupyterlab-omnisci) [![](https://img.shields.io/npm/v/jupyterlab-omnisci.svg?style=flat-square)](https://www.npmjs.com/package/jupyterlab-omnisci)

![example](./screenshot.png)

## Installation

First, install JupyterLab and `pymapd` as well the `jupyterlab-omnisci` Python package and
`jupyterlab-omnisci` JupyterLab extension:

```bash
conda install -c conda-forge jupyterlab pymapd

pip install jupyterlab-omnisci git+https://github.com/ibis-project/ibis.git@5672feb8516d56c7c9d9faacc083c6e6f9b953fa
jupyter labextension install jupyterlab-omnisci
```

Then launch Jupyter Lab:

```bash
jupyter lab
```

## Executing SQL Queries

You can open an OmiSci SQL editor by going to **File > New > OmniSci SQL Editor** or clicking the icon on the launcher.

Input your database credentials by clicking on the blue icon on the right:

![](./sqlcon.png)

Then you can input an SQL query and hit the triangle to see the results:

![](./sql.png)

To set a default connection that will be saved and used for new editors, go to **Settings > Set Default Omnisci Connection...**.

## Creating Visualizations

Check out the [introduction notebook](./notebooks/Introduction.ipynb) to see how to use OmniSci within your notebooks [![](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight/jupyterlab-omnisci/master?urlpath=lab/tree/notebooks/Introduction.ipynb).

## FAQ

1. Something isn't working right. What should I do?
   _[Open an issue!](https://github.com/Quansight/jupyterlab-omnisci/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D+) It's likely not your fault, many of these integrations are new and we need your feedback to understand what use cases are important_.

## Installing from source

To install from source, run the following in a terminal:

```bash
git clone https://github.com/Quansight/jupyterlab-omnisci
cd jupyterlab-omnisci
conda create -f environment.yml
conda activate jupyterlab-omnisci
jlpm install
jlpm run build
jupyter labextension install .
pip install -e .
```

## Releasing

### Python Package

First bump the version number in `setup.py`.

Then, follow the [setuptools docs](https://setuptools.readthedocs.io/en/latest/setuptools.html#distributing-a-setuptools-based-project) on how to release
a package:

```bash
pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# try installing
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple jupyterlab_omnisci
# upload for real
twine upload dist/*
```
