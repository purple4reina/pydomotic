import codecs
import os.path

from setuptools import find_packages, setup

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('version'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="automaton",
    version=get_version("automaton/version.py"),
    url="https://github.com/purple4reina/automaton",
    author="Rey Abolofia",
    author_email="purple4reina@gmail.com",
    #keywords="gosund,smartlife,tuya,iot,api,sdk,python",
    #description="Python API for controling Gosund smart devices",
    #long_description=read("README.md"),
    #long_description_content_type="text/markdown",
    license="MIT",
    project_urls={
        "Source": "https://github.com/purple4reina/automaton",
        "Bug Tracker": "https://github.com/purple4reina/automaton/issues",
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=[
        "astral>=3.0,<4.0",
        "boto3>=1.26.3,<2.0",  # TODO: only if requested
        "gosundpy>=0.2.0,<1.0",  # TODO: only if provider requested
        "PyYAML>=6.0,<7.0",
    ],
    packages=find_packages(),
    python_requires=">=3.7, <4",
)
