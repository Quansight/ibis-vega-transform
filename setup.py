"""Setup script for Ibis Vega Transform."""

# Standard library imports
import ast
import os

# Third party imports
import setuptools

# Constants
HERE = os.path.abspath(os.path.dirname(__file__))


def get_version(module="ibis_vega_transform"):
    """Get version."""
    data = read(os.path.join(HERE, module, "__init__.py"))
    lines = data.split("\n")
    for line in lines:
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split("=")[-1].strip())
            return version


def read(path, encoding="utf-8"):
    """
    Read file specified by path relative to file and return content.
    """
    path = os.path.join(HERE, path)

    content = ""
    if os.path.exists(path):
        with open(path, encoding=encoding) as fh:
            content = fh.read()

    return content


setuptools.setup(
    name="ibis-vega-transform",
    version=get_version(),
    url="https://github.com/Quansight/ibis-vega-transform",
    author="Ian Rose and Saul Shanabrook",
    author_email="ian.rose@quansight.com",
    license="Apache-2.0 license",
    description="Evaluate Vega transforms using Ibis expressions",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "altair>=4.0.0",
        "altair-transform",
        "ibis-framework>=1.3.0",
        "jaeger-client",
        "jupyter_jaeger>=1.0.3",
        "jupyterlab>=2.0.0",
        "mypy_extensions",
        "pymapd",
        "tornado",
        "typing_extensions",
        "vega_datasets",
    ],
    extras_require={"dev": ["black"]},
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
