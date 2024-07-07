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
        raise RuntimeError('Unable to find version string.')

def get_extras_require():
    # providers
    airthings = []
    ecobee = []
    fujitsu = ['pyfujitsu>=0.9.0,<1.0']
    moen = ['pyflowater>=0.5.2,<1.0', 'retry>=0.9.2,<1.0']
    tuya = ['gosundpy>=0.7.0,<1.0']

    # features
    s3 = ['boto3>=1.26.3,<2.0']
    tz = ['timezonefinder>=6.1.8,<7.0']

    return {
        'airthings': airthings,
        'ecobee': ecobee,
        'fujitsu': fujitsu,
        'moen': moen,
        'tuya': tuya,
        's3': s3,
        'tz': tz,
        'all': airthings + ecobee + fujitsu + moen + tuya + s3 + tz,
    }

setup(
    name='pydomotic',
    version=get_version('pydomotic/version.py'),
    url='https://github.com/purple4reina/pydomotic',
    author='Rey Abolofia',
    author_email='purple4reina@gmail.com',
    keywords='iot,python,home,automation,smart,domotic',
    description=('Python library for home automation execution, enabling '
            'seamless control and management of your IoT devices'),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/purple4reina/pydomotic',
        'Bug Tracker': 'https://github.com/purple4reina/pydomotic/issues',
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=[
        'PyYAML>=6.0,<7.0',
        'astral>=3.0,<4.0',
        'croniter>=1.3.15,<2.0',
        'pyowm>=3.3.0,<4.0',
    ],
    extras_require=get_extras_require(),
    packages=find_packages(),
    python_requires='>=3.8,<4',
)
