import setuptools
"""
Build script for setuptools. This script provides information (such as
the package distribution name, package version, and files to include) to
setuptools about the package.
"""
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ucop-utils-pkg',
    version='2.0.7',
    author='Annapurna Annadatha',
    author_email='annapurna.annadatha@ucop.edu',
    description='UCOP utilities package for the AWS Data Lake projects.',
    long_description='A Python package for a set of UCOP utilities that support the AWS Data Lake projects.',
    long_description_content_type='text/markdown',
    license='Completely unsupported freeware.',
    url='https://github.com/sdsc-sherlock/rdms/tree/main/ucop-util-pkg',
    download_url='https://pypi.org/search/?q=ucop-utils-pkg',
    packages=setuptools.find_packages(),
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires='>=3.8',
)
