"""
Setup configuration for Certbox.
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read version from package __init__.py
init_path = Path(__file__).parent / "certbox" / "__init__.py"
with open(init_path, "r", encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in certbox/__init__.py")

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="certbox",
    version=version,
    author="GISCE-TI",
    author_email="devel@gisce.net",
    description="X.509 Certificate Management Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gisce/certbox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "certbox=certbox.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)