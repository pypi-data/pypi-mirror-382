# © Copyright Databand.ai, an IBM Company 2022

from os import path

import setuptools

from setuptools.config import read_configuration


BASE_PATH = path.dirname(__file__)
CFG_PATH = path.join(BASE_PATH, "setup.cfg")

config = read_configuration(CFG_PATH)
version = config["metadata"]["version"]

setuptools.setup(
    name="dbnd-airflow-export",
    package_dir={"": "src"},
    # we are not requiring airflow, as this plugin should be installed into existing airflow deployment
    install_requires=["dbnd==" + version, "dbnd-airflow==" + version],
    entry_points={},
)
