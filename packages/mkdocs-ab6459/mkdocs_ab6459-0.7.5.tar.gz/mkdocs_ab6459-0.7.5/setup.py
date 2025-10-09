from setuptools import setup, find_packages
import argparse

with open("README.md", "r") as fh:
    long_desc = fh.read()

setup(
    name="mkdocs_ab6459",
    version="0.7.5",
    url='https://github.coventry.ac.uk/ab6459/mkdocs_ab6459',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Documentation',
        'Topic :: Text Processing',
    ],
    install_requires=[
        'mkdocs',
    ],
    license='MIT',
    description='A custom theme for Coventry University modules.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    author='Ian Cornelius',
    author_email='ab6459@coventry.ac.uk',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'ab6459 = mkdocs_ab6459',
        ]
    },
    zip_safe=False
)