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
