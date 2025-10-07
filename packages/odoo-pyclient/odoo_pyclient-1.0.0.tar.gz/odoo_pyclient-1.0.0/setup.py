"""
Setup file for OdooPyClient package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="odoo-pyclient",
    version="1.0.0",
    author="Mohamed Helmy",
    description="Python client for Odoo using the requests library and JSON-RPC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohamed-helmy/OdooPyClient",
    packages=find_packages(),
    py_modules=["odoo_client"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="odoo erp client api jsonrpc",
    project_urls={
        "Bug Reports": "https://github.com/mohamed-helmy/OdooPyClient/issues",
        "Source": "https://github.com/mohamed-helmy/OdooPyClient",
    },
)
