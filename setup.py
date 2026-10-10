from setuptools import find_packages, setup

setup(
    version="1.1.0",
    packages=find_packages(),
    package_data={
        "aberoth_ephemeris.ephemeris": ["variables.json"],
    },
)
