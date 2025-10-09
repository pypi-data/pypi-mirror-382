"""Setup script for GeomKit package."""

import re
from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
init_file = this_directory / "geomkit" / "__init__.py"
version_match = re.search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', init_file.read_text(encoding="utf-8"), re.MULTILINE
)
if version_match:
    version = version_match.group(1)
else:
    raise RuntimeError("Unable to find version string in geomkit/__init__.py")

setup(
    name="geomkit",
    version=version,
    author="Mohamed Sajith",
    author_email="mmssajith@gmail.com",
    description="A comprehensive Python library for 2D and 3D geometric operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmssajith/geomkit",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "geometry",
        "mathematics",
        "computational-geometry",
        "2d",
        "3d",
        "vector",
        "point",
        "line",
        "circle",
        "ellipse",
        "polygon",
        "triangle",
        "shapes",
        "geometric-algorithms",
        "math-library",
        "transformation-matrix",
        "bezier-curve",
        "convex-hull",
        "bounding-box",
        "sphere",
        "cube",
    ],
    project_urls={
        "Homepage": "https://github.com/mmssajith/geomkit",
        "Bug Tracker": "https://github.com/mmssajith/geomkit/issues",
        "Documentation": "https://github.com/mmssajith/geomkit#readme",
        "Source Code": "https://github.com/mmssajith/geomkit",
        "Changelog": "https://github.com/mmssajith/geomkit/blob/main/CHANGELOG.md",
    },
    package_data={
        "geomkit": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
)
