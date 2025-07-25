"""
Setup script for SpaceTraders Python Client
"""

from setuptools import setup, find_packages

with open("spacetraders_client/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("spacetraders_client/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="spacetraders-client",
    version="1.0.0",
    author="SpaceTraders Community",
    description="A typed, object-oriented Python client for the SpaceTraders API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Connor-Harkness/Spacetraders-python-ui-api",
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
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "isort",
            "mypy",
        ],
    },
    include_package_data=True,
    package_data={
        "spacetraders_client": ["*.md", "*.txt"],
    },
)