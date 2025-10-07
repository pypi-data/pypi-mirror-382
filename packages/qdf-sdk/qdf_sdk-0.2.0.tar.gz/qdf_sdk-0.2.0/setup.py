"""
Setup configuration for QDF SDK
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Extract production requirements only (exclude dev dependencies)
prod_requirements = [
    req for req in requirements
    if not any(dev in req for dev in ["pytest", "black", "mypy", "pandas"])
]

setup(
    name="qdf-sdk",
    version="0.2.0",
    author="QuantDeFi",
    author_email="dev@quantdefi.com",
    description="Python SDK for QuantDeFi Pool Rankings and Analytics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QuantDeFi/qdf-sdk",
    project_urls={
        "Bug Reports": "https://github.com/QuantDeFi/qdf-sdk/issues",
        "Source": "https://github.com/QuantDeFi/qdf-sdk",
        "Documentation": "https://docs.quantdefi.com",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=prod_requirements,
    extras_require={
        "pandas": ["pandas>=2.0.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "mypy>=1.4.0",
            "twine>=3.8.0",
            "build>=0.10.0",
        ],
        "all": ["pandas>=2.0.0"],
    },
    keywords="defi, blockchain, crypto, pools, rankings, analytics, api, sdk",
    include_package_data=True,
    zip_safe=False,
)