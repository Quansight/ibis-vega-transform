# ibis-vega-transform

Python evaluation of Vega transforms using Ibis expressions.

For inspiration, see https://github.com/jakevdp/altair-transform

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
