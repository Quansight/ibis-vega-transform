# ibis-vega-transform <br /> [![binder logo](https://beta.mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight/ibis-vega-transform/master?urlpath=lab/tree/examples/vega-compiler.ipynb) [![Tests](https://github.com/Quansight/ibis-vega-transform/workflows/Run%20tests%20on%20example%20notebooks/badge.svg)](https://github.com/Quansight/ibis-vega-transform/actions?query=workflow%3A%22Run+tests+on+example+notebooks%22) [![](https://img.shields.io/pypi/v/ibis-vega-transform.svg?style=flat-square)](https://pypi.python.org/pypi/ibis-vega-transform) [![](https://img.shields.io/npm/v/ibis-vega-transform.svg?style=flat-square)](https://www.npmjs.com/package/ibis-vega-transform)

Python evaluation of Vega transforms using Ibis expressions.

For inspiration, see https://github.com/jakevdp/altair-transform

## Getting started

```sh
pip install ibis-vega-transform
jupyter labextension install ibis-vega-transform
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

# or ibis.pandas if ibis version < 1.4
connection = ibis.backends.pandas.connect({'source': source })
table = connection.table('source')

alt.Chart(table).mark_bar().encode(
    x='a',
    y='b'
)
```

Check out the notebooks in the [`./examples/`](./examples/) directory to see
some options using interactive charts and the OmniSci backend.

## Usage

Importing `ibis_vega_transform` sets the `altair` renderer and data transformer to `"ibis"`. It also monkeypatches the Ibis chart constructor to handle `ibis` expressions.

Now, whenever you pass an `ibis` expression to a chart constructor, it will use the custom ibis renderer, which pushes all data aggregates to ibis, instead of in the browser.

You can also set a debug flag, to have it instead pull in the first N rows of the ibis expression and use the default renderer. This is useful to see how the default pipeline would have rendered your chart. If you are getting some error, I reccomend setting this first to see if the error was on the Altair side or on the `ibis-vega-transform` side. If the fallback chart rendered correctly, it means the error is in this codebase. If it's wrong, then the error is in your code or in altair or in Vega.

```python
# enable fallback mode
ibis_vega_transform.set_fallback(True)
# disable fallback mode (the default)
ibis_vega_transform.set_fallback(False)
```

### Tracing

If you want to see traces of the interactiosn for debugging and performance analysis,
install the `jaeger-all-in-one` binary and the `jupyterlab-server-proxy`
lab extension to see the Jaeger icon in the launcher.

```bash
conda install jaeger -c conda-forge
jupyter labextension install jupyterlab-server-proxy-saulshanabrook
```

The Jaeger server won't actually be started until a HTTP request is sent to it,
so before you run your visualization, click the "Jaeger" icon in the JupyterLab launcher or go to
`/jaeger` to open the UI. Then run your visualization and you should see the traces appear in Jaeger.

You also will likely have to increase the max UDP packet size on your OS to [accomdate for the large logs](https://github.com/jaegertracing/jaeger-client-node/issues/124#issuecomment-324222456):

### Mac

```sh
# Edit now
sudo sysctl net.inet.udp.maxdgram=200000
# Edit on restart
echo net.inet.udp.maxdgram=200000 | sudo tee -a /etc/sysctl.conf
```

## Development

To install from source, run the following in a terminal:

```sh
git clone git@github.com:Quansight/ibis-vega-transform.git

cd ibis-vega-transform
conda env create -f binder/environment.yml
conda activate ibis-vega-transform

pip install -e ".[dev]"
jlpm
jupyter labextension install . --no-build

jupyter lab --watch
jlpm run watch
```

A pre-commit hook is installed usig Husky (Git > 2.13 is required!) to format files.

Run the formatting tools at any time using:

```sh
black ibis_vega_transform
jlpm run prettier
```

### Tracing

We are using [`jupyter-jaeger`](https://github.com/Quansight/jupyter-jaeger) to trace each interaction
for benchmarking.
