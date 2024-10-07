from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="aberoth-ephemeris",
    version="1.0.1",
    author="Jeremiah Vandagrift",
    url="https://github.com/jvandag/aberoth-ephemeris",
    author_email="",
    description="Provides predictions for scroll and lunar events in the MMO Aberoth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["aberoth", "solar system", "orbs", "ephemeris", "predictions", "MMO", "Overheard"],
    packages=find_packages(),
    package_data={
        "aberoth_ephemeris.ephemeris": [".variables.json"],
    },
    install_requires=[
    "numpy==1.26.4",
    "python-dotenv==1.0.1",
    "Flask==3.0.3",
    "Flask-Cors==4.0.1",
    "waitress==3.0.0"
    ],
    include_package_data=True,
)
