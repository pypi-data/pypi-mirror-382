from setuptools import setup, find_packages

setup(
    name="simplecord",
    version="0.0.1",
    author="Muhammad Usman",
    author_email="usmank.personal@outlook.com",
    description="A simple 3d rendering engine for python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/m-usman-k/simplecord",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
)
