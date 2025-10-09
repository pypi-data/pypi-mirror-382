
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "advantech_edge",
    version = "1.0.1",
    author = 'Advantech Co., Ltd.',
    author_email = '',
    packages = find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires = ["setuptools"]
)
