#!/usr/bin/env python
"""Utility functions for dbt-erd."""

import os


def ensure_directory_exists(directory_path):
    """Create a directory if it doesn't exist.

    Args:
        directory_path: Path to the directory

    Returns:
        True if the directory was created, False if it already exists
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    return False


def find_sql_files(directory_path):
    """Find all SQL files in a directory and its subdirectories.

    Args:
        directory_path: Path to the directory

    Returns:
        List of paths to SQL files
    """
    sql_files = []
    for root, _dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".sql"):
                sql_files.append(os.path.join(root, file))
    return sql_files


def get_model_name_from_file(file_path):
    """Extract model name from file path.

    Args:
        file_path: Path to the model file

    Returns:
        Model name without file extension
    """
    return os.path.basename(file_path).replace(".sql", "")


def get_model_directory(model_path, project_dir):
    """Get the parent directory for models to look for YAML files.

    Args:
        model_path: Path to the model directory
        project_dir: Path to the project directory

    Returns:
        Path to the parent directory of the models
    """
    # If model_path is a subdirectory of models, go one level up
    if "models/" in model_path:
        return os.path.dirname(model_path)

    # Try to find the models directory
    if os.path.exists(os.path.join(project_dir, "models")):
        return os.path.join(project_dir, "models")

    # Default to the provided path
    return model_path


def get_formatted_details(model_name, fact_file, dimension_tables):
    """Get a formatted string with details about the model.

    Args:
        model_name: Name of the model
        fact_file: Path to the model file
        dimension_tables: List of dimension table names

    Returns:
        Formatted string with model details
    """
    details = f"Processing {model_name}...\n"

    if dimension_tables:
        details += "Found {} dimension references: {}\n".format(
            len(dimension_tables), ", ".join(dimension_tables)
        )
    else:
        details += "Warning: No dimension references found.\n"

    return details
