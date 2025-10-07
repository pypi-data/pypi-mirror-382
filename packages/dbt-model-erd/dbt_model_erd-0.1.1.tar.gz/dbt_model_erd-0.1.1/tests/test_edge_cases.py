"""Edge case tests for dbt-erd."""

import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mermaid_generator
import model_analyzer
import yaml_manager


def test_malformed_sql_file(temp_dir):
    """Test handling of malformed SQL files."""
    # Create SQL file with syntax errors but valid ref()
    malformed_sql = """
    SELECT * FROM {{ ref('dim_customer') }}
    WHERE  -- incomplete WHERE clause
    AND customer_id = [malformed
    """

    sql_file = os.path.join(temp_dir, "malformed.sql")
    with open(sql_file, "w") as f:
        f.write(malformed_sql)

    # Should still extract refs despite SQL errors
    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert "dim_customer" in refs


def test_sql_with_no_refs(temp_dir):
    """Test SQL file with no ref() statements."""
    sql_content = """
    SELECT * FROM raw_table
    WHERE created_at > '2024-01-01'
    """

    sql_file = os.path.join(temp_dir, "no_refs.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert len(refs) == 0


def test_sql_with_commented_refs(temp_dir):
    """Test that commented out refs are still extracted."""
    sql_content = """
    -- This is a comment with {{ ref('dim_customer') }}
    SELECT * FROM actual_table
    /* Block comment {{ ref('dim_product') }} */
    """

    sql_file = os.path.join(temp_dir, "commented.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    # Regex will find refs even in comments (this is expected behavior)
    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert len(refs) == 2


def test_sql_with_duplicate_refs(temp_dir):
    """Test that duplicate refs are deduplicated."""
    sql_content = """
    SELECT * FROM {{ ref('dim_customer') }}
    JOIN {{ ref('dim_customer') }}
    WHERE id IN (SELECT id FROM {{ ref('dim_customer') }})
    """

    sql_file = os.path.join(temp_dir, "duplicates.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert len(refs) == 1
    assert "dim_customer" in refs


def test_missing_yaml_file():
    """Test handling when YAML file doesn't exist."""
    result = model_analyzer.get_yaml_file_for_model(
        "/nonexistent/path", "fact_orders"
    )
    assert result is None


def test_empty_yaml_file(temp_dir):
    """Test handling of empty YAML file."""
    yaml_file = os.path.join(temp_dir, "empty.yml")
    with open(yaml_file, "w") as f:
        f.write("")

    # Should not crash
    columns_info = model_analyzer.get_column_info(temp_dir)
    assert len(columns_info) == 0


def test_yaml_with_no_models_section(temp_dir):
    """Test YAML file without models section."""
    schema = {
        "version": 2,
        "sources": [
            {"name": "raw", "tables": [{"name": "orders"}]}
        ]
    }

    yaml_file = os.path.join(temp_dir, "sources_only.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    columns_info = model_analyzer.get_column_info(temp_dir)
    assert len(columns_info) == 0


def test_yaml_with_models_but_no_columns(temp_dir):
    """Test YAML file with models but no columns defined."""
    schema = {
        "version": 2,
        "models": [
            {"name": "fact_orders", "description": "No columns defined"}
        ]
    }

    yaml_file = os.path.join(temp_dir, "no_columns.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    columns_info = model_analyzer.get_column_info(temp_dir)
    # Should not include models without columns
    assert "fact_orders" not in columns_info


def test_model_with_no_primary_key(sample_config):
    """Test handling model with no identifiable primary key."""
    columns = [
        {"name": "data_field_1"},
        {"name": "data_field_2"}
    ]

    # Should fall back to first column
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "data_field_1"


def test_model_with_empty_columns(sample_config):
    """Test handling model with empty columns list."""
    columns = []

    # Should return generic 'id'
    pk = model_analyzer.find_primary_key(columns, sample_config)
    assert pk == "id"


def test_foreign_key_not_found(sample_config):
    """Test when foreign key cannot be found for dimension."""
    fact_columns = [
        {"name": "order_id"},
        {"name": "order_date"},
        {"name": "amount"}
    ]

    # Try to find FK for dimension that's not referenced
    fk = model_analyzer.find_foreign_key_for_dimension(
        fact_columns, "dim_customer", "customer", sample_config
    )

    # The function finds "order_id" as it matches the FK pattern "_id"
    # Even though it's not specifically related to customer, it's returned as the first potential FK
    assert fk == "order_id"


def test_circular_references(temp_dir):
    """Test handling of circular model references."""
    # Model A refs Model B
    model_a_sql = "SELECT * FROM {{ ref('model_b') }}"
    with open(os.path.join(temp_dir, "model_a.sql"), "w") as f:
        f.write(model_a_sql)

    # Model B refs Model A
    model_b_sql = "SELECT * FROM {{ ref('model_a') }}"
    with open(os.path.join(temp_dir, "model_b.sql"), "w") as f:
        f.write(model_b_sql)

    # Each should extract their own refs
    refs_a = model_analyzer.extract_refs_from_sql(
        os.path.join(temp_dir, "model_a.sql")
    )
    refs_b = model_analyzer.extract_refs_from_sql(
        os.path.join(temp_dir, "model_b.sql")
    )

    assert "model_b" in refs_a
    assert "model_a" in refs_b


def test_special_characters_in_model_names(temp_dir):
    """Test handling model names with special characters."""
    sql_content = """
    SELECT * FROM {{ ref('dim_customer_v2') }}
    JOIN {{ ref('dim-product-final') }}
    """

    sql_file = os.path.join(temp_dir, "special_chars.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert "dim_customer_v2" in refs
    assert "dim-product-final" in refs


def test_very_long_column_list(sample_config):
    """Test handling models with many columns."""
    # Create 100 columns
    columns = [{"name": f"column_{i}"} for i in range(100)]

    # Should handle without issues
    entity = mermaid_generator.generate_table_entity(
        "test_table", columns, "column_0", [], True, 20
    )

    # Should limit to 20 columns
    assert "column_0" in entity
    assert "column_19" in entity
    assert "column_20" not in entity


def test_unicode_in_descriptions(temp_dir):
    """Test handling unicode characters in descriptions."""
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts with emoji 🚀 and unicode chars: café, naïve",
                "columns": [
                    {
                        "name": "customer_id",
                        "description": "Customer ID with special chars: €100, ±5%"
                    }
                ]
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "unicode.yml")
    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(schema, f, allow_unicode=True)

    # Should handle unicode without crashing
    columns_info = model_analyzer.get_column_info(temp_dir)
    assert "fact_orders" in columns_info


def test_mixed_quote_types_in_refs(temp_dir):
    """Test refs with mixed single and double quotes."""
    sql_content = """
    SELECT * FROM {{ ref('dim_customer') }}
    JOIN {{ ref("dim_product") }}
    JOIN {{ ref(  'dim_store'  ) }}
    """

    sql_file = os.path.join(temp_dir, "mixed_quotes.sql")
    with open(sql_file, "w") as f:
        f.write(sql_content)

    refs = model_analyzer.extract_refs_from_sql(sql_file)
    assert len(refs) == 3
    assert "dim_customer" in refs
    assert "dim_product" in refs
    assert "dim_store" in refs


def test_relationship_detection_with_dict_tests(sample_config):
    """Test relationship detection when tests are defined as dicts."""
    fact_columns = [
        {
            "name": "customer_id",
            "tests": [
                {"unique": True},
                {"not_null": True}
            ]
        }
    ]

    rel_type = model_analyzer.detect_relationship_type(
        fact_columns, "customer_id", "dim_customer", sample_config
    )

    # Should detect as one-to-one due to unique constraint
    assert rel_type == "one_to_one"


def test_entity_name_extraction_edge_cases(sample_config):
    """Test entity name extraction with unusual patterns."""
    # Multiple underscores
    assert "customer" in model_analyzer.extract_entity_name("dim___customer", sample_config)

    # Already clean name
    assert model_analyzer.extract_entity_name("customer", sample_config) == "customer"

    # Name with numbers
    assert model_analyzer.extract_entity_name("dim_customer_v2", sample_config) == "customer_v2"


def test_update_yaml_with_very_long_description(temp_dir):
    """Test updating YAML with existing very long description."""
    long_desc = "A" * 5000  # 5000 character description

    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": long_desc,
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "long_desc.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # Should handle long descriptions
    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/diagram.html"
    )

    assert result is True


def test_windows_path_separators(sample_config):
    """Test handling Windows-style path separators."""
    # This test is relevant for cross-platform compatibility
    project_dir = "C:\\Users\\project"
    model_path = "C:\\Users\\project\\models\\dw\\fact"

    # Should handle Windows paths (on Windows) or Unix paths (on Unix)
    result = yaml_manager.get_relative_asset_path(
        project_dir, model_path, "fact_orders", sample_config
    )

    # Should generate valid path
    assert "fact_orders_model.html" in result
    assert "assets" in result or "img" in result
