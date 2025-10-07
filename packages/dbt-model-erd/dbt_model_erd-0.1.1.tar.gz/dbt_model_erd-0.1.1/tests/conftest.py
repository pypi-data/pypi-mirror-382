"""Pytest fixtures for dbt-erd tests."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def sample_config():
    """Return a sample configuration for testing."""
    return {
        "naming": {
            "dimension_patterns": ["dim_", "__dim_", "_dim_"],
            "fact_patterns": ["fact_", "__fact_", "_fact_"],
            "dim_pk_patterns": ["_pk", "_key", "_id"],
            "fact_pk_patterns": ["_pk", "_key", "_id"],
            "fact_fk_patterns": ["_fk", "_id"],
            "table_prefixes": ["dw__", "mart__", "stg__"],
        },
        "visualization": {
            "max_dimensions": 10,
            "show_columns": True,
            "column_limit": 20,
        },
        "mermaid": {
            "theme": "default",
            "direction": "LR",
            "outputs": {
                "mmd": True,
                "html": True,
            },
            "interactive": True,
            "style": {
                "fact_table_fill": "#f5f5f5",
                "dimension_table_fill": "#e8f4f8",
            },
            "embed": {
                "type": "html",
            },
        },
        "paths": {"asset_base": "assets/img", "yaml_extension": ".yml"},
        "relationships": {
            "default_type": "many_to_one",
            "detect_from_naming": True,
            "show_labels": True,
            "multiple_fk_handling": "first",
        },
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def sample_yml_file(temp_dir):
    """Create a sample YAML file with model definitions."""
    content = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table",
                "columns": [
                    {
                        "name": "order_id",
                        "description": "Primary key for orders",
                        "tests": ["unique", "not_null"],
                    },
                    {
                        "name": "customer_id",
                        "description": "Foreign key to customer dimension",
                        "tests": ["not_null"],
                    },
                    {"name": "order_date", "description": "Date of the order"},
                    {"name": "amount", "description": "Order amount"},
                ],
            },
            {
                "name": "dim_customer",
                "description": "Customer dimension table",
                "columns": [
                    {
                        "name": "customer_id",
                        "description": "Primary key for customers",
                        "tests": ["unique", "not_null"],
                    },
                    {"name": "first_name", "description": "Customer's first name"},
                    {"name": "last_name", "description": "Customer's last name"},
                    {"name": "email", "description": "Customer's email address"},
                ],
            },
        ],
    }

    filepath = os.path.join(temp_dir, "schema.yml")
    with open(filepath, "w") as f:
        yaml.dump(content, f)

    return filepath


@pytest.fixture
def sample_sql_file(temp_dir):
    """Create a sample SQL file with references."""
    content = """
    WITH customer AS (
        SELECT * FROM {{ ref('dim_customer') }}
    ),
    
    final AS (
        SELECT
            order_id,
            customer_id,
            order_date,
            amount
        FROM orders
        LEFT JOIN customer USING (customer_id)
    )
    
    SELECT * FROM final
    """

    filepath = os.path.join(temp_dir, "fact_orders.sql")
    with open(filepath, "w") as f:
        f.write(content)

    return filepath
