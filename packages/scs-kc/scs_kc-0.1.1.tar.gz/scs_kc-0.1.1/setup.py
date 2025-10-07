from setuptools import setup, find_packages

setup(
    name="scs-kc",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    description="Package for Kerr-cat optimization with supercoefficients",
    python_requires=">=3.10",
)
