# setup.py
from setuptools import setup, find_packages

setup(
    name="xlcalcmodel",
    version="3.06.7",
    author="Derek Pierson",
    author_email="derek.r.pierson@gmail.com",
    description="A Python-based Excel calculation engine with advanced function support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mustseetv314/xlcalcmodel",
    packages=find_packages(),
    install_requires=[
        'jsonpickle',
        'numpy',
        'pandas',
        'openpyxl',
        'numpy-financial',
        'mock',
        'scipy',
        'requests',
        'xlwings',
        'yearfrac',
        'python-dateutil',
        'tqdm'
    ],
    python_requires=">=3.7",
)
