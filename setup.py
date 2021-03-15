"""Setup script for Ibis Vega Transform."""
import ast
import json
import os
from pathlib import Path

import setuptools
import jupyter_packaging
from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    skip_if_exists,
)
from packaging.version import parse

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "ibis-vega-transform"

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


# Get our version
with (HERE / "package.json").open() as f:
    version = str(parse(json.load(f)["version"]))

long_description = (HERE / "README.md").read_text(errors="ignore")

# Representative files that should exist after a successful build
lab_path = HERE / name / "labextension"

jstargets = [
    str(lab_path / "package.json"),
]

package_data_spec = {name: ["*"]}

labext_name = "ibis-vega-transform"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str(HERE), "install.json"),
    (
        "etc/jupyter/jupyter_server_config.d",
        "jupyter-config/jupyter_server_config.d",
        "jupyterlab_git.json",
    ),
    (
        "etc/jupyter/jupyter_notebook_config.d",
        "jupyter-config/jupyter_notebook_config.d",
        "jupyterlab_git.json",
    ),
]

cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)

js_command = combine_commands(
    install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
    ensure_targets(jstargets),
)

is_repo = (HERE / ".git").exists()
if is_repo:
    cmdclass["jsdeps"] = js_command
else:
    cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)

setup_args = dict(
    name="ibis-vega-transform",
    version=get_version(),
    url="https://github.com/Quansight/ibis-vega-transform",
    author="Ian Rose and Saul Shanabrook",
    author_email="ian.rose@quansight.com",
    license="Apache-2.0 license",
    description="Evaluate Vega transforms using Ibis expressions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "altair>=4.0.0",
        "altair-transform",
        "ibis-framework>=1.3.0",
        "jaeger-client",
        "jupyter_jaeger>=1.0.3",
        "jupyterlab==3.*",
        "jupyter_packaging~=0.7.12",
        "mypy_extensions",
        "pymapd==0.24.*",  # NOTE: remove this pinning when ibis v2 is ready
        "sqlalchemy<1.4",
        "tornado",
        "typing_extensions",
        "vega_datasets",
    ],
    extras_require={"dev": ["black"]},
    python_requires=">=3.7,<3.8",
    include_package_data=True,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass=cmdclass,
)


if __name__ == '__main__':
    setuptools.setup(**setup_args)
