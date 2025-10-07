"""Tests for mermaid_generator.py functions."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mermaid_generator


def test_get_column_type():
    """Test inferring column type from name or description."""
    # Test date type inference
    assert mermaid_generator.get_column_type({"name": "order_date"}) == "date"
    assert mermaid_generator.get_column_type({"name": "timestamp"}) == "date"
    assert mermaid_generator.get_column_type({"name": "dt_updated"}) == "date"
    
    # Add created_at with description
    assert mermaid_generator.get_column_type({"name": "created_at", "description": "timestamp when record was created"}) == "date"
    
    # Test float type inference
    assert mermaid_generator.get_column_type({"name": "order_amount"}) == "float"
    assert mermaid_generator.get_column_type({"name": "unit_price"}) == "float"
    assert mermaid_generator.get_column_type({"name": "item_cost"}) == "float"
    assert mermaid_generator.get_column_type({"name": "total_revenue"}) == "float"
    
    # Test int type inference
    assert mermaid_generator.get_column_type({"name": "customer_id"}) == "int"
    assert mermaid_generator.get_column_type({"name": "item_count"}) == "int"
    assert mermaid_generator.get_column_type({"name": "product_num"}) == "int"
    
    # Test boolean type inference
    assert mermaid_generator.get_column_type({"name": "is_active"}) == "boolean"
    assert mermaid_generator.get_column_type({"name": "has_discount"}) == "boolean"
    
    # Test inference from description
    assert mermaid_generator.get_column_type({"name": "foo", "description": "Date of order"}) == "date"
    assert mermaid_generator.get_column_type({"name": "bar", "description": "Decimal value for price"}) == "float"
    assert mermaid_generator.get_column_type({"name": "baz", "description": "Integer count of items"}) == "int"
    assert mermaid_generator.get_column_type({"name": "qux", "description": "Boolean flag for status"}) == "boolean"
    
    # Test default to string
    assert mermaid_generator.get_column_type({"name": "customer_name"}) == "string"
    assert mermaid_generator.get_column_type({"name": "email"}) == "string"


def test_generate_table_entity():
    """Test generating Mermaid entity definition for a table."""
    table_name = "dim_customer"
    columns = [
        {"name": "customer_id", "tests": ["unique", "not_null"]},
        {"name": "first_name"},
        {"name": "last_name"},
        {"name": "email"}
    ]
    pk_name = "customer_id"
    fk_names = []
    
    # Test with columns shown
    entity = mermaid_generator.generate_table_entity(
        table_name, columns, pk_name, fk_names, True, 10
    )
    
    # Should include table name
    assert "    dim_customer {" in entity
    
    # Should include PK column
    assert "        int customer_id PK" in entity
    
    # Should include regular columns
    assert "        string first_name" in entity
    assert "        string last_name" in entity
    assert "        string email" in entity
    
    # Test with columns hidden
    entity = mermaid_generator.generate_table_entity(
        table_name, columns, pk_name, fk_names, False, 10
    )
    
    # Should only include PK
    assert "        string customer_id PK" in entity
    assert "        string first_name" not in entity
    
    # Test with column limit
    columns = [{"name": f"col_{i}"} for i in range(15)]
    entity = mermaid_generator.generate_table_entity(
        table_name, columns, pk_name, fk_names, True, 10
    )
    
    # Should include only first 10 columns
    for i in range(10):
        assert f"        string col_{i}" in entity
    
    # Should not include columns beyond limit
    for i in range(10, 15):
        assert f"        string col_{i}" not in entity


def test_generate_relationship():
    """Test generating Mermaid relationship between tables."""
    config = {
        "relationships": {
            "show_labels": True,
            "relationship_types": {
                "many_to_one": {
                    "description": "Many-to-One",
                    "start_marker": "many",
                    "end_marker": "one"
                }
            }
        }
    }
    
    # Test with FK label
    rel = mermaid_generator.generate_relationship(
        "dim_customer", "fact_orders", "customer_id", "many_to_one", config
    )
    assert '    dim_customer ||--o{ fact_orders : "customer_id"' in rel
    
    # Test without FK label
    config["relationships"]["show_labels"] = False
    rel = mermaid_generator.generate_relationship(
        "dim_customer", "fact_orders", "customer_id", "many_to_one", config
    )
    assert "    dim_customer ||--o{ fact_orders" in rel
    assert '"customer_id"' not in rel
    
    # Test with different relationship types
    rel_mappings = {
        "many_to_one": "||--o{",
        "one_to_many": "}o--||",
        "many_to_many": "}o--o{",
        "one_to_one": "||--||",
        "zero_one_to_many": "|o--o{",
        "zero_one_to_one": "|o--||",
        "zero_many_to_one": "||--o|"
    }
    
    config["relationships"]["show_labels"] = True
    for rel_type, symbol in rel_mappings.items():
        rel = mermaid_generator.generate_relationship(
            "dim_customer", "fact_orders", "customer_id", rel_type, config
        )
        assert f"    dim_customer {symbol} fact_orders" in rel
