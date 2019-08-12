import os
import setuptools


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    return open(path, encoding=encoding).read() if os.path.exists(path) else ""


setuptools.setup(
    name="ibis-vega-transform",
    version="0.1.0",
    url="https://github.com/Quansight/ibis-vega-transform",
    author="Ian Rose and Saul Shanabrook",
    author_email="ian.rose@quansight.com",
    license="Apache-2.0 license",
    description="Evaluate Vega transforms using Ibis expressions",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "altair-transform",
        "ibis-framework",
        "mypy_extensions",
        "typing_extensions",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
