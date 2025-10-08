"""
Setup script for ManageX XML Signing SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="managex-xml-sdk",
    version="1.0.0",
    author="ManageX Development Team",
    author_email="dev@managex.com",
    description="Complete XML Digital Signing SDK with PKI certificate validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/managex/xml-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.8",
        "lxml>=4.6.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "hsm": ["PyKCS11>=1.5.0"],
        "windows": ["pywin32>=227"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "managex-xml=managex_xml_sdk.cli:main",
        ],
    },
    keywords=[
        "xml", "digital-signature", "pki", "certificate", "hsm", "pfx",
        "cryptography", "signing", "validation", "xmldsig", "x509"
    ],
    project_urls={
        "Bug Reports": "https://github.com/managex/xml-sdk/issues",
        "Source": "https://github.com/managex/xml-sdk",
        "Documentation": "https://docs.managex.com/xml-sdk",
    },
)