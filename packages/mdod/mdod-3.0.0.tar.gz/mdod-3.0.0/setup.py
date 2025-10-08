from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mdod",
    version="3.0.0",
    packages=find_packages(),
    package_data={"": ["*"]},  
    install_requires=[],
    author="Z Shen",
    author_email="626456708@qq.com",
    description="MDOD, Multi-Dimensional data Outlier Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",  
    license="BSD 3-Clause License",
    url="https://github.com/mddod/mdod",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)