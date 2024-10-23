# setup.py
from setuptools import setup, find_packages

setup(
    name='vispy',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'graphviz',
    ],
    entry_points={
        'console_scripts': [
            'vispy=vispy.cli:main',
        ],
    },
    author='Luke Friedrichs',
    author_email='lukefriedrichs@gmail.com',
    description='A Python package to analyze class hierarchies and generate visualizations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lckylke/vispy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
