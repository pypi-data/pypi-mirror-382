"""
Setup script for ManageX XML Signing SDK
"""

import os
import sys
from setuptools import setup, find_packages

# Read version from __init__.py
def get_version():
    version_dict = {}
    with open(os.path.join("managex_xml_sdk", "__init__.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                exec(line, version_dict)
                return version_dict["__version__"]
    return "1.0.0"

version = {"__version__": get_version()}

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt"""
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Handle platform-specific requirements
                if "sys_platform" in line:
                    requirements.append(line)
                else:
                    requirements.append(line.split(";")[0].strip())
        return requirements

# Core requirements (cross-platform)
install_requires = [
    "cryptography>=3.4.8",
    "lxml>=4.6.3",
    "requests>=2.25.1",
]

# Platform-specific extras
extras_require = {
    "windows": [
        "pywin32>=228",
    ],
    "hsm": [
        "PyKCS11>=1.5.12",
    ],
    "dev": [
        "pytest>=6.2.5",
        "pytest-cov>=2.12.1",
        "black>=21.9b0",
        "flake8>=3.9.2",
        "mypy>=0.910",
    ],
    "docs": [
        "sphinx>=4.2.0",
        "sphinx-rtd-theme>=1.0.0",
    ]
}

# Add all extras for complete installation
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="managex-xml-sdk",
    version=version["__version__"],
    author="Aniket Chaturvedi",
    author_email="chaturvedianiket007@gmail.com",
    description="A comprehensive Python SDK for digital certificate management and XML digital signing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aniketc068/managex_xml_sdk",
    project_urls={
        "Bug Reports": "https://github.com/Aniketc068/managex_xml_sdk/issues",
        "Source": "https://github.com/Aniketc068/managex_xml_sdk",
        "Documentation": "https://github.com/Aniketc068/managex_xml_sdk/wiki",
        "Discussions": "https://github.com/Aniketc068/managex_xml_sdk/discussions",
    },
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords=[
        "xml", "digital-signature", "certificate", "pkcs11", "hsm", "pfx", "windows-store",
        "cryptography", "security", "signing", "managex", "enterprise", "pki"
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "managex-xml-sign=managex_xml_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "managex_xml_sdk": [
            "*.md",
            "examples/*.py",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    maintainer="Aniket Chaturvedi",
    maintainer_email="chaturvedianiket007@gmail.com",
)