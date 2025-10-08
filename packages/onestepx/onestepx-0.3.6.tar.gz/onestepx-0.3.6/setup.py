from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="onestepx",
    version="0.3.6",
    description="Instant hierarchical collapse to terminal node (O(1) traversal)",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Maulud Sadiq",
    author_email="mauludsadiq@gmail.com",
    license="MIT",
    url="https://github.com/mauludsadiq/onestep",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
