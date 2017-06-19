__author__ = 'Jovan Cejovic <jovan.cejovic@sbgenomics.com>'
__date__ = '30 January 2017'
__copyright__ = 'Copyright (c) 2017 Seven Bridges Genomics'

import io
from setuptools import setup, find_packages

version = "0.1"

# no requirements for now
install_requires = []

setup(
    name='sparqb',
    version=version,
    description='Python SPARQL query builder library',
    install_requires=install_requires,
    long_description=io.open('README.md', 'r').read(),
    platforms=['Windows', 'POSIX', 'MacOS'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='developer@sbgenomics.com',
    url='https://github.com/sbg/sparqb',
    license='Apache Software License 2.0',
    include_package_data=True,
    packages=find_packages(exclude=["*.test"]),
    keywords=['sevenbridges', 'sbg', 'sparql', 'rdf', 'query', 'builder'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering :: Semantic Web',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)