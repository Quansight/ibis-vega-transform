"""Setup script for Ibis Vega Transform."""
import ast
import json
import os
from pathlib import Path

import setuptools
from jupyter_packaging import (
    npm_builder,
    ensure_targets,
    combine_commands,
    skip_if_exists,
)
from packaging.version import parse


# # Representative files that should exist after a successful build
# lab_path = HERE / name / "labextension"

# jstargets = [
#     str(lab_path / "package.json"),
# ]

# package_data_spec = {name: ["*"]}

# labext_name = "ibis-vega-transform"

# data_files_spec = [
#     ("share/jupyter/labextensions/%s" % labext_name, str(lab_path), "**"),
#     ("share/jupyter/labextensions/%s" % labext_name, str(HERE), "install.json"),
#     (
#         "etc/jupyter/jupyter_server_config.d",
#         "jupyter-config/jupyter_server_config.d",
#         "ibis_vega_transform.json",
#     ),
#     (
#         "etc/jupyter/jupyter_notebook_config.d",
#         "jupyter-config/jupyter_notebook_config.d",
#         "ibis_vega_transform.json",
#     ),
# ]

# cmdclass = create_cmdclass(
#     "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
# )

# js_command = combine_commands(
#     install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
#     ensure_targets(jstargets),
# )

# is_repo = (HERE / ".git").exists()
# if is_repo:
#     cmdclass["jsdeps"] = js_command
# else:
#     cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)


try:
    from jupyter_packaging import wrap_installers, npm_builder

    pre_builder = npm_builder(build_cmd="build:pre-install", npm=["jlpm"])
    pre_builder.__name__ = "pre_develop"

    post_builder = npm_builder(build_cmd="build:post-install", npm=["jlpm"])
    post_builder.__name__ = "post_develop"

    cmdclass = wrap_installers(
        pre_develop=pre_builder,
        pre_dist=pre_builder,
        post_develop=post_builder,
        post_dist=post_builder
    )
except ImportError:
    cmdclass = {}

if __name__ == '__main__':
    setuptools.setup(cmdclass=cmdclass)
