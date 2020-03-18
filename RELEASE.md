# Releasing

## Using Rever

Make sure your current environment has [rever](https://regro.github.io/rever-docs/) installed.

```bash
conda install rever -c conda-forge
```

Run checks before to make sure things are in order.

```bash
rever check
```

Delete the rever folder to start a clean release.

```bash
rm -rf rever/
```

Run rever with the type version (major|minor|patch) to update.

### Major release

If the current version is `3.0.0.dev0`, running:

```bash
rever major
```

Will produce version `4.0.0` and update the dev versions to `4.0.0.dev0`

### Minor release

If the current version is `3.0.0.dev0`, running:

```bash
rever minor
```

Will produce version `3.1.0` and update the dev versions to `3.1.0.dev0`

### Patch release

If the current version is `3.0.0.dev0`, running:

```bash
rever patch
```

Will produce version `3.0.1` and update the dev versions to `3.0.1.dev0`

### Important

- In case some of the steps appear as completed, delete the `rever` folder.

```bash
rm -rf rever/
```

- Some of the intermediate steps will ask for feedback, like checking the example notebooks.

## Manual Process

First create a test environment:

```bash
conda env remove -n tmp-ibis-vega-transform --yes
conda env create -f binder/environment.yml --name tmp-ibis-vega-transform
conda install --name tmp-ibis-vega-transform black twine yarn wheel --channel conda-forge --yes --quiet
```

Then bump the Python version in `setup.py` and upload a test version:

```bash
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
rm out.tgz
git add package.json setup.py
git commit -m 'Version <new version>'
git tag <new version>
git push
git push --tags
```
