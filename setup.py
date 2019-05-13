import setuptools

setuptools.setup(
    name="ibis-vega-transform",
    version="0.1.0",
    url="",
    author="Ian Rose",
    author_email="ian.rose@quansight.com",
    license="BSD 3-Clause",
    description="Turn vega transforms into Ibis expressions",
    packages=setuptools.find_packages(),
    install_requires=["ibis-framework"],
    python_requires=">=3.6",
    include_package_data=True,
)
