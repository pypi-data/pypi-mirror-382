# setup.py
from pathlib import Path
import re
from setuptools import setup, find_packages

ROOT = Path(__file__).parent

def read_text(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def read_version():
    # Expect: src/nepali_toolkit/_version.py -> __version__ = "x.y.z"
    m = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]',
        read_text("src/nepali_toolkit/_version.py"),
        re.M,
    )
    if not m:
        raise RuntimeError("Cannot find __version__ in src/nepali_toolkit/_version.py")
    return m.group(1)

setup(
    name="nepali-toolkit",
    version=read_version(),
    description="Production-ready utilities for Nepali: BS calendar & holidays, script tools, gazetteer, units, treks.",
    long_description=read_text("README.md"),
    long_description_content_type="text/markdown",
    author="Sujit Khanal",
    author_email="thesujitkhanal@gmail.com",
    url="https://github.com/yourorg/nepali-toolkit",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "python-dateutil>=2.8.2",
        "pytz>=2024.1",
        "regex>=2024.5.15",
        "pydantic>=2.7"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "mypy>=1.0",
            "ruff>=0.4",
            "build>=1.0",
            "twine>=4.0",
        ],
    },
    include_package_data=True,  # works with MANIFEST.in
    package_data={
        # JSON data files bundled inside the wheel
        "nepali_toolkit.bs": ["data/*.json"],
        "nepali_toolkit.scripts": ["data/*.json"],
        "nepali_toolkit.holiday": ["data/*.json"],
        "nepali_toolkit.gazetteer": ["data/*.json"],
        "nepali_toolkit.trek": ["data/*.json"],
        "nepali_toolkit.units": ["data/*.json"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: English",
        "Natural Language :: Nepali",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/yourorg/nepali-toolkit/issues",
        "Source": "https://github.com/yourorg/nepali-toolkit",
    },
)
