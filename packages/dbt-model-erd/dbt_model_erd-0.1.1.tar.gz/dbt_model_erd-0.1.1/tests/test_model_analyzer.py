"""Tests for model_analyzer.py functions."""

import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import model_analyzer


def test_extract_refs_from_sql(temp_dir):
    """Test extracting ref() statements from SQL files."""
    # Create a SQL file with various ref patterns
    sql_content = """
    WITH customers AS (
        SELECT * FROM {{ ref('dim_customer') }}
    ),
    products AS (
        SELECT * FROM {{ ref("dim_product") }}
    ),
    stores AS (
        SELECT * FROM {{ref('dim_store')}}
    ),
    final AS (
        SELECT
            c.customer_id,
            p.product_id,
            s.store_id
        FROM {{ ref('dim_customer') }}  -- Duplicate ref
    )
    SELECT * FROM final
    """

    sql_file = os.path.join(temp_dir, "test.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    # Extract refs
    refs = model_analyzer.extract_refs_from_sql(sql_file)

    # Should find 3 unique refs (deduplicates dim_customer)
    assert len(refs) == 3
    assert "dim_customer" in refs
    assert "dim_product" in refs
    assert "dim_store" in refs


def test_extract_refs_from_sql_no_refs(temp_dir):
    """Test extracting refs from SQL with no ref statements."""
    sql_content = "SELECT * FROM raw_table"

    sql_file = os.path.join(temp_dir, "test.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert len(refs) == 0


def test_get_column_info(temp_dir):
    """Test scanning YAML files for column information."""
    # Create test YAML files in subdirectories
    models_dir = os.path.join(temp_dir, "models")
    fact_dir = os.path.join(models_dir, "fact")
    dim_dir = os.path.join(models_dir, "dim")

    os.makedirs(fact_dir)
    os.makedirs(dim_dir)

    # Create fact schema
    fact_schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "columns": [
                    {"name": "order_id"},
                    {"name": "customer_id"},
                ]
            }
        ]
    }

    with open(os.path.join(fact_dir, "schema.yml"), "w") as f:
        yaml.dump(fact_schema, f)

    # Create dimension schema
    dim_schema = {
        "version": 2,
        "models": [
            {
                "name": "dim_customer",
                "columns": [
                    {"name": "customer_id"},
                    {"name": "first_name"},
                    {"name": "last_name"},
                ]
            }
        ]
    }

    with open(os.path.join(dim_dir, "schema.yml"), "w") as f:
        yaml.dump(dim_schema, f)

    # Get column info
    columns_info = model_analyzer.get_column_info(models_dir)

    # Should find both models
    assert "fact_orders" in columns_info
    assert "dim_customer" in columns_info

    # Check column counts
    assert len(columns_info["fact_orders"]) == 2
    assert len(columns_info["dim_customer"]) == 3


def test_get_yaml_file_for_model(temp_dir):
    """Test finding the YAML file for a specific model."""
    models_dir = os.path.join(temp_dir, "models")
    os.makedirs(models_dir)

    # Create schema with multiple models
    schema = {
        "version": 2,
        "models": [
            {"name": "fact_orders", "columns": []},
            {"name": "fact_sales", "columns": []},
        ]
    }

    schema_path = os.path.join(models_dir, "schema.yml")
    with open(schema_path, "w") as f:
        yaml.dump(schema, f)

    # Find YAML for fact_orders
    found_yaml = model_analyzer.get_yaml_file_for_model(models_dir, "fact_orders")
    assert found_yaml == schema_path

    # Find YAML for fact_sales
    found_yaml = model_analyzer.get_yaml_file_for_model(models_dir, "fact_sales")
    assert found_yaml == schema_path

    # Try to find non-existent model
    found_yaml = model_analyzer.get_yaml_file_for_model(models_dir, "nonexistent")
    assert found_yaml is None


def test_is_fact_table(sample_config):
    """Test identifying fact tables."""
    # Test with fact prefix
    assert model_analyzer.is_fact_table("fact_orders", "/path/to/models/fact_orders.sql", sample_config)

    # Test with __fact__ pattern
    assert model_analyzer.is_fact_table("dw__fact_sales", "/path/to/models/sales.sql", sample_config)

    # Test with 'fact' in path
    assert model_analyzer.is_fact_table("orders", "/path/to/fact/orders.sql", sample_config)

    # Test dimension table
    assert not model_analyzer.is_fact_table("dim_customer", "/path/to/models/dim_customer.sql", sample_config)


def test_is_dimension_table(sample_config):
    """Test identifying dimension tables."""
    # Test with dim prefix
    assert model_analyzer.is_dimension_table("dim_customer", sample_config)

    # Test with __dim__ pattern
    assert model_analyzer.is_dimension_table("dw__dim_product", sample_config)

    # Test fact table
    assert not model_analyzer.is_dimension_table("fact_orders", sample_config)


def test_extract_entity_name(sample_config):
    """Test extracting entity name from table names."""
    # Test dimension table
    assert model_analyzer.extract_entity_name("dim_customer", sample_config) == "customer"

    # Test fact table
    assert model_analyzer.extract_entity_name("fact_orders", sample_config) == "orders"

    # Test with table prefix
    assert model_analyzer.extract_entity_name("dw__dim_product", sample_config) == "product"

    # Test with __dim__ pattern
    assert model_analyzer.extract_entity_name("mart__dim_store", sample_config) == "store"


def test_find_primary_key(sample_config):
    """Test finding primary key from column definitions."""
    # Test with unique test
    columns = [
        {"name": "customer_id", "tests": ["unique", "not_null"]},
        {"name": "first_name"},
    ]
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "customer_id"

    # Test with primary_key test
    columns = [
        {"name": "order_id", "tests": ["primary_key"]},
        {"name": "customer_id"},
    ]
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "order_id"

    # Test with naming pattern
    columns = [
        {"name": "customer_pk"},
        {"name": "first_name"},
    ]
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "customer_pk"

    # Test fallback to first column
    columns = [
        {"name": "some_column"},
        {"name": "another_column"},
    ]
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "some_column"


def test_find_foreign_key_for_dimension(sample_config):
    """Test finding foreign key that references a dimension."""
    fact_columns = [
        {"name": "order_id"},
        {"name": "customer_id"},
        {"name": "product_id"},
    ]

    # Find FK for dim_customer
    fk = model_analyzer.find_foreign_key_for_dimension(
        fact_columns, "dim_customer", "customer", sample_config
    )
    assert fk == "customer_id"

    # Find FK for dim_product
    fk = model_analyzer.find_foreign_key_for_dimension(
        fact_columns, "dim_product", "product", sample_config
    )
    assert fk == "product_id"


def test_find_all_foreign_keys_for_dimension(sample_config):
    """Test finding all possible foreign keys for a dimension."""
    # Test with multiple potential FKs
    fact_columns = [
        {"name": "order_id"},
        {"name": "customer_id"},
        {"name": "shipping_customer_id"},
    ]

    fks = model_analyzer.find_all_foreign_keys_for_dimension(
        fact_columns, "dim_customer", "customer", sample_config
    )

    # Should find both customer FKs
    assert len(fks) == 2
    assert "customer_id" in fks
    assert "shipping_customer_id" in fks


def test_find_foreign_key_with_description(sample_config):
    """Test finding FK using column description."""
    fact_columns = [
        {"name": "order_id"},
        {"name": "cust_ref", "description": "Foreign key to customer dimension"},
    ]

    fks = model_analyzer.find_all_foreign_keys_for_dimension(
        fact_columns, "dim_customer", "customer", sample_config
    )

    # Should find cust_ref based on description
    assert "cust_ref" in fks


def test_detect_relationship_type(sample_config):
    """Test detecting relationship types from column info."""
    # Test one-to-one (unique FK)
    fact_columns = [
        {"name": "customer_id", "tests": ["unique", "not_null"]},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )
    assert rel_type == "one_to_one"

    # Test many-to-one (default)
    fact_columns = [
        {"name": "customer_id", "tests": ["not_null"]},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )
    assert rel_type == "many_to_one"

    # Test zero-one-to-many (nullable FK - has some tests but no not_null)
    fact_columns = [
        {"name": "customer_id", "tests": ["accepted_values"]},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )
    assert rel_type == "zero_one_to_many"

    # Test many-to-one with no tests (defaults to many_to_one)
    fact_columns = [
        {"name": "customer_id"},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )
    assert rel_type == "many_to_one"

    # Test many-to-one with empty tests list (also defaults to many_to_one)
    fact_columns = [
        {"name": "customer_id", "tests": []},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )
    assert rel_type == "many_to_one"

    # Test many-to-many (plural FK)
    fact_columns = [
        {"name": "customers_id"},
    ]
    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customers_id", "dim_customer", sample_config
    )
    assert rel_type == "many_to_many"
