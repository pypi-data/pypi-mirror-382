#!/usr/bin/env python
from setuptools import setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dbt-model-erd",
    use_scm_version={
        "write_to": "_version.py",
        "version_scheme": "post-release",
        "local_scheme": "no-local-version",
    },
    author="Entechlog",
    description="Generate entity-relationship diagrams for dbt models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/entechlog/dbt-model-erd",
    py_modules=[
        "__init__",
        "config",
        "dbt_erd",
        "mermaid_generator",
        "mermaid_renderer",
        "model_analyzer",
        "utils",
        "yaml_manager",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.8",
    setup_requires=[
        "setuptools_scm>=6.0",
    ],
    install_requires=[
        "ruamel.yaml>=0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "ruff>=0.1.0",
            "pyyaml>=5.1",  # Used by tests for creating test fixtures
        ],
    },
    entry_points={
        "console_scripts": [
            "dbt-model-erd=dbt_erd:main",
        ],
    },
    include_package_data=True,
)
