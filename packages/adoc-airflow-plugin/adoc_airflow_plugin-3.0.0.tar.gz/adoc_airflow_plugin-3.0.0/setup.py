#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from setuptools import find_namespace_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

__version__ = "3.0.0"

requirements = [
    "acceldata-sdk>=4.8.0"
]

setup(
    name="adoc_airflow_plugin",
    version=__version__,
    description="Acceldata Airflow Listener Plugin",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="acceldata",
    packages=find_namespace_packages(include=["acceldata.*"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    zip_safe=False,
    keywords="acceldata",
    entry_points={
        "airflow.plugins": [
            "AcceldataListenerPlugin = acceldata.airflow.plugin:AcceldataListenerPlugin"
        ]
    }
)
