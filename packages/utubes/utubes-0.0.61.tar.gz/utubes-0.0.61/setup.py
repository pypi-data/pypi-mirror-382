from setuptools import find_packages
from setuptools import setup
from Utubes import appname
from Utubes import version
from Utubes import install
from Utubes import pythons
from Utubes import mention
from Utubes import DATA01
from Utubes import DATA02
from Utubes import DATA03

with open("README.md", "r") as o:
    description = o.read()

setup(
    url=DATA01,
    name=appname,
    version=version,
    keywords=mention,
    description=DATA03,
    classifiers=DATA02,
    python_requires=pythons,
    packages=find_packages(),
    install_requires=install,
    long_description=description,
    long_description_content_type="text/markdown")
