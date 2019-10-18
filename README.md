# ibis-vega-transform <br /> [![binder logo](https://beta.mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight/ibis-vega-transform/master?urlpath=lab/tree/examples/vega-compiler.ipynb) [![](https://img.shields.io/pypi/v/ibis-vega-transform.svg?style=flat-square)](https://pypi.python.org/pypi/ibis-vega-transform) [![](https://img.shields.io/npm/v/ibis-vega-transform.svg?style=flat-square)](https://www.npmjs.com/package/ibis-vega-transform)


Python evaluation of Vega transforms using Ibis expressions.

For inspiration, see https://github.com/jakevdp/altair-transform


## Getting started

```bash
pip install ibis-vega-transform
jupyter labextension  install ibis-vega-transform
```

Then in a notebook, import the Python package and pass in an ibis expression
to a Altair chart:

```python
import altair as alt
import ibis_vega_transform
import ibis
import pandas as pd


source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
})

connection = ibis.pandas.connect({'source': source })
table = connection.table('source')

alt.Chart(table).mark_bar().encode(
    x='a',
    y='b'
)
```

Check out the notebooks in the [`./examples/`](./examples/] directory to see
some options using interactive charts and the OmniSci backend.

## Development

To install from source, run the following in a terminal:




```bash
git clone git@github.com:Quansight/ibis-vega-transform.git

cd ibis-vega-transform
conda env create -f binder/environment.yml
conda activate ibis-vega-transform

pip install -e .[dev]
jlpm
jupyter labextension install . --no-build


jupyter lab --watch
jlpm run build:watch
```

To format all the files:

```bash
black ibis_vega_transform
jlpm run prettier
```


### Tracing

1. Install [Jaeger binary](https://www.jaegertracing.io/download/)
2. `jaeger-all-in-one`
3. `env JAEGER_SERVICE_NAME=browser python -m ibis_vega_transform.tracing_server`
4. `open http://localhost:16686/`
5. Display charts and look at traces

## Releasing

First create a test environment:

```bash
conda create -n tmp -c conda-forge nodejs
conda activate tmp
```

Then bump the Python version in `setup.py` and upload a test version:

```bash
pip install --upgrade setuptools wheel twine
rm -rf dist/
python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install the test version in your new environment:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ibis-vega-transform
```

Now bump the version for the Javascript package in `package.json`. The run a build,
create a tarball, and install it as a JupyterLab extension:

```bash
yarn run build
yarn pack --filename out.tgz
jupyter labextension install out.tgz
```

Now open JupyterLab and run through all the notebooks in `examples` to make sure
they still render correctly.

Now you can publish the Python package:

```bash
twine upload dist/*
```

And publish the node package:

```bash
npm publish out.tgz
```

And add a git tag for the release and push:

```bash
git tag <new version>
git push
git push --tags
```