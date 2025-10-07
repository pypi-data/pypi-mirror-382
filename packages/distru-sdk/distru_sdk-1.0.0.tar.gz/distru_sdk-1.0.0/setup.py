"""Setup script for distru-sdk package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from package
version = {}
with open("distru_sdk/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="distru-sdk",
    version=version.get("__version__", "1.0.0"),
    description="Official Python SDK for the Distru API - Cannabis supply chain management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Distru Inc.",
    author_email="support@distru.com",
    url="https://github.com/DistruApp/distru-api-sdk",
    project_urls={
        "Documentation": "https://github.com/DistruApp/distru-api-sdk/tree/main/python",
        "Source": "https://github.com/DistruApp/distru-api-sdk",
        "Issues": "https://github.com/DistruApp/distru-api-sdk/issues",
        "Homepage": "https://distru.com",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        'typing-extensions>=4.0.0; python_version < "3.11"',
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "responses>=0.23.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.23.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
    keywords=[
        "distru",
        "api",
        "sdk",
        "cannabis",
        "supply-chain",
        "inventory",
        "compliance",
        "metrc",
        "biotrack",
        "rest",
        "client",
    ],
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
