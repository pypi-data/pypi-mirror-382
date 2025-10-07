"""Tests for utils.py functions."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


def test_ensure_directory_exists():
    """Test creating a directory that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test_dir")
        
        # Directory doesn't exist yet
        assert not os.path.exists(test_dir)
        
        # Create it
        result = utils.ensure_directory_exists(test_dir)
        
        # Function should return True and directory should exist
        assert result is True
        assert os.path.exists(test_dir)
        
        # Try creating it again
        result = utils.ensure_directory_exists(test_dir)
        
        # Function should return False since directory already exists
        assert result is False


def test_find_sql_files(temp_dir):
    """Test finding SQL files in a directory."""
    # Create some SQL files
    sql_file1 = os.path.join(temp_dir, "model1.sql")
    sql_file2 = os.path.join(temp_dir, "model2.sql")
    txt_file = os.path.join(temp_dir, "not_sql.txt")
    
    # Create a subdirectory with a SQL file
    subdir = os.path.join(temp_dir, "subdir")
    os.makedirs(subdir)
    sql_file3 = os.path.join(subdir, "model3.sql")
    
    # Create the files
    for file in [sql_file1, sql_file2, txt_file, sql_file3]:
        with open(file, "w") as f:
            f.write("test content")
    
    # Find SQL files
    sql_files = utils.find_sql_files(temp_dir)
    
    # Should find 3 SQL files
    assert len(sql_files) == 3
    
    # Should contain all SQL files
    assert sql_file1 in sql_files
    assert sql_file2 in sql_files
    assert sql_file3 in sql_files
    
    # Should not contain text file
    assert txt_file not in sql_files


def test_get_model_name_from_file():
    """Test extracting model name from file path."""
    file_path = "/path/to/models/dim_customer.sql"
    model_name = utils.get_model_name_from_file(file_path)
    assert model_name == "dim_customer"


def test_get_model_directory():
    """Test getting the parent directory for models."""
    # Test with model_path that includes "models/"
    project_dir = "/path/to/project"
    model_path = "/path/to/project/models/dw/fact"
    parent_dir = utils.get_model_directory(model_path, project_dir)
    assert parent_dir == "/path/to/project/models/dw"
    
    # Test with project_dir that has a models directory
    with tempfile.TemporaryDirectory() as tmpdir:
        models_dir = os.path.join(tmpdir, "models")
        os.makedirs(models_dir)
        
        model_path = os.path.join(tmpdir, "some/other/path")
        parent_dir = utils.get_model_directory(model_path, tmpdir)
        assert parent_dir == models_dir


def test_get_formatted_details():
    """Test formatting model details."""
    model_name = "fact_orders"
    fact_file = "/path/to/models/fact_orders.sql"
    dimension_tables = ["dim_customer", "dim_product"]
    
    details = utils.get_formatted_details(model_name, fact_file, dimension_tables)
    
    # Should include model name and dimension tables
    assert "Processing fact_orders" in details
    assert "dimension references: dim_customer, dim_product" in details
    
    # Test with no dimension tables
    details = utils.get_formatted_details(model_name, fact_file, [])
    assert "Warning: No dimension references found" in details
