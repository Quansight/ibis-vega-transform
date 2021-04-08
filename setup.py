"""
ibis_vega_transform setup
"""
import json
import os

from jupyter_packaging import (
    create_cmdclass, install_npm, ensure_targets,
    combine_commands, skip_if_exists
)
import setuptools

HERE = os.path.abspath(os.path.dirname(__file__))

# The name of the project
name="ibis_vega_transform"

# Get our version
with open(os.path.join(HERE, 'package.json')) as f:
    version = json.load(f)['version']

lab_path = os.path.join(HERE, name, "labextension")

# Representative files that should exist after a successful build
jstargets = [
    os.path.join(lab_path, "package.json"),
]

package_data_spec = {
    name: [
        "*"
    ]
}

labext_name = "ibis_vega_transform"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, lab_path, "**"),
    ("share/jupyter/labextensions/%s" % labext_name, HERE, "install.json"),("etc/jupyter/jupyter_server_config.d",
     "jupyter-config", "ibis_vega_transform.json"),

]

cmdclass = create_cmdclass("jsdeps",
    package_data_spec=package_data_spec,
    data_files_spec=data_files_spec
)

js_command = combine_commands(
    install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
    ensure_targets(jstargets),
)

is_repo = os.path.exists(os.path.join(HERE, ".git"))
if is_repo:
    cmdclass["jsdeps"] = js_command
else:
    cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = dict(
    name="ibis-vega-transform",
    version=version,
    url="https://github.com/Quansight/ibis-vega-transform",
    author="OmniSci/Quansight",
    description="Evaluate Vega transforms using Ibis expressions.",
    long_description= long_description,
    long_description_content_type="text/markdown",
    cmdclass=cmdclass,
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyterlab>=3.0.0rc13,==3.*",
        "setuptools>=46.4.0",
        "altair>=4.0.0",
        "altair-transform",
        "ibis-framework>=1.3.0",
        "jaeger-client",
        "jupyter_jaeger @ git+https://github.com/Quansight/jupyter-jaeger.git@master",
        "jupyterlab_server",
        "mypy_extensions",
        "nbclassic>=0.2",
        "opentracing",
        # NOTE: remove pymapd pinning when ibis v2 is ready
        "pymapd==0.24.*",
        # NOTE: current ibis version doesn't work with sqlalchemy 1.4
        "sqlalchemy<1.4",
        "tornado",
        "typing_extensions",
        "vega_datasets",
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.7,<3.8",
    license="Apache-2.0",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Framework :: Jupyter",
    ],
)


if __name__ == "__main__":
    setuptools.setup(**setup_args)
