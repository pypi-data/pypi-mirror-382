"""Setup script for Vultus Serpentis framework."""

from setuptools import setup, find_packages
import os

# Read README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vultus-serpentis",
    version="1.0.0",
    description="A comprehensive Python framework for building GUI applications with Observable patterns, Event Bus, Actions, Validation, and Commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vultus Serpentis Team",
    url="https://github.com/yourusername/vultus-serpentis",
    project_urls={
        "Documentation": "https://github.com/yourusername/vultus-serpentis/blob/main/README.md",
        "Source": "https://github.com/yourusername/vultus-serpentis",
        "Bug Tracker": "https://github.com/yourusername/vultus-serpentis/issues",
    },
    # Find packages - look in parent directory
    packages=find_packages(where=".."),
    package_dir={"": ".."},
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords="gui framework observable event-bus commands validation actions tkinter mvc",
)
