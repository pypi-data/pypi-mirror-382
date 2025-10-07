"""Tests for yaml_manager.py functions."""

import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import yaml_manager


def test_update_model_yaml_add_new_diagram(temp_dir):
    """Test adding a new diagram section to model description."""
    # Create a YAML file
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table",
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # Update the YAML
    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    # Should succeed
    assert result is True

    # Read back and verify
    with open(yaml_file) as f:
        updated_schema = yaml.safe_load(f)

    desc = updated_schema["models"][0]["description"]
    assert "## Data Model Diagram" in desc
    assert "[View interactive diagram](/assets/img/fact/fact_orders_model.html)" in desc


def test_update_model_yaml_replace_existing_diagram(temp_dir):
    """Test replacing an existing diagram section."""
    # Create a YAML file with existing diagram
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table\n\n## Data Model Diagram\n\n[Old diagram](old.html)\n",
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # Update the YAML
    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    assert result is True

    # Read back and verify
    with open(yaml_file) as f:
        updated_schema = yaml.safe_load(f)

    desc = updated_schema["models"][0]["description"]
    assert "## Data Model Diagram" in desc
    assert "[View interactive diagram](/assets/img/fact/fact_orders_model.html)" in desc
    assert "old.html" not in desc


def test_update_model_yaml_preserve_other_sections(temp_dir):
    """Test that updating diagram preserves other documentation sections."""
    # Create a YAML file with multiple sections
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table\n\n## Usage\n\nThis table is for analytics.\n\n## Data Model Diagram\n\n[Old diagram](old.html)\n\n## Notes\n\nSome important notes.",
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # Update the YAML
    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    assert result is True

    # Read back and verify
    with open(yaml_file) as f:
        updated_schema = yaml.safe_load(f)

    desc = updated_schema["models"][0]["description"]
    # Should preserve other sections
    assert "## Usage" in desc
    assert "This table is for analytics" in desc
    # Diagram should be updated
    assert "[View interactive diagram](/assets/img/fact/fact_orders_model.html)" in desc
    assert "old.html" not in desc


def test_update_model_yaml_model_not_found(temp_dir):
    """Test updating a model that doesn't exist in YAML."""
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table",
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # Try to update non-existent model
    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_sales", "/assets/img/fact/fact_sales_model.html"
    )

    # Should fail
    assert result is False


def test_update_model_yaml_file_not_found():
    """Test updating a YAML file that doesn't exist."""
    result = yaml_manager.update_model_yaml(
        "/nonexistent/schema.yml", "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    # Should fail
    assert result is False


def test_update_model_yaml_invalid_yaml(temp_dir):
    """Test updating an invalid YAML file."""
    yaml_file = os.path.join(temp_dir, "invalid.yml")

    # Create invalid YAML
    with open(yaml_file, "w") as f:
        f.write("invalid: yaml: content: [unclosed")

    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    # Should fail
    assert result is False


def test_update_model_yaml_no_models_section(temp_dir):
    """Test updating a YAML file with no models section."""
    schema = {
        "version": 2,
        "sources": []
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    result = yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    # Should fail
    assert result is False


def test_get_relative_asset_path(sample_config):
    """Test generating relative asset paths."""
    project_dir = "/path/to/project"
    model_path = "/path/to/project/models/dw/fact"
    model_name = "fact_orders"

    # Test default HTML extension
    path = yaml_manager.get_relative_asset_path(
        project_dir, model_path, model_name, sample_config
    )

    assert path == "/assets/img/dw/fact/fact_orders_model.html"


def test_get_relative_asset_path_custom_extension(sample_config):
    """Test generating relative asset paths with custom extension."""
    project_dir = "/path/to/project"
    model_path = "/path/to/project/models/dw/fact"
    model_name = "fact_orders"

    # Test custom extension
    path = yaml_manager.get_relative_asset_path(
        project_dir, model_path, model_name, sample_config, ".mmd"
    )

    assert path == "/assets/img/dw/fact/fact_orders_model.mmd"


def test_get_relative_asset_path_nested_models(sample_config):
    """Test generating relative asset paths for deeply nested models."""
    project_dir = "/path/to/project"
    model_path = "/path/to/project/models/marts/finance/monthly"
    model_name = "fact_revenue"

    path = yaml_manager.get_relative_asset_path(
        project_dir, model_path, model_name, sample_config
    )

    assert path == "/assets/img/marts/finance/monthly/fact_revenue_model.html"


def test_get_relative_asset_path_different_asset_base():
    """Test generating paths with different asset base config."""
    config = {
        "paths": {
            "asset_base": "docs/diagrams"
        }
    }

    project_dir = "/path/to/project"
    model_path = "/path/to/project/models/dw/fact"
    model_name = "fact_orders"

    path = yaml_manager.get_relative_asset_path(
        project_dir, model_path, model_name, config
    )

    assert path == "/docs/diagrams/dw/fact/fact_orders_model.html"


def test_update_model_yaml_no_extra_empty_lines(temp_dir):
    """Test that running update multiple times doesn't add extra empty lines.

    This test reproduces the bug where users reported empty lines being
    added to descriptions on each run, even when the diagram already exists.
    """
    # Create a YAML file with existing ERD link (simulating user's YAML after first run)
    yaml_content = """version: 2
models:
- name: fact_orders
  description: 'Order-level fact table aggregated from order items


    ## Data Model Diagram


    [View interactive diagram](/assets/img/dw/fact/fact_orders_model.html)

    '
  columns:
  - name: order_id
    description: Surrogate key for orders
"""

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        f.write(yaml_content)

    # Read original to count newlines
    with open(yaml_file) as f:
        original = f.read()

    original_newline_count = original.count('\n\n\n')

    # Run the update function (simulating running dbt-erd again)
    result = yaml_manager.update_model_yaml(
        yaml_file,
        "fact_orders",
        "/assets/img/dw/fact/fact_orders_model.html"
    )

    assert result is True

    # Read the updated file
    with open(yaml_file) as f:
        updated = f.read()

    updated_newline_count = updated.count('\n\n\n')

    # Should NOT add extra empty lines
    assert updated_newline_count <= original_newline_count, \
        f"Extra empty lines added: {original_newline_count} -> {updated_newline_count}"

    # Run it AGAIN to make sure it's idempotent
    result = yaml_manager.update_model_yaml(
        yaml_file,
        "fact_orders",
        "/assets/img/dw/fact/fact_orders_model.html"
    )

    assert result is True

    with open(yaml_file) as f:
        second_update = f.read()

    second_newline_count = second_update.count('\n\n\n')

    # Should STILL not add extra empty lines
    assert second_newline_count <= original_newline_count, \
        f"Extra empty lines added on second run: {original_newline_count} -> {second_newline_count}"


def test_update_model_yaml_preserve_double_quotes(temp_dir):
    """Test that double quotes in descriptions are preserved.

    This test reproduces the bug where users reported that double-quoted
    descriptions were being converted to single quotes or unquoted.
    """
    # Create a YAML file with double-quoted descriptions
    yaml_content = '''version: 2
models:
- name: fact_orders
  description: "Order-level fact table"
  columns:
  - name: order_id
    description: "Surrogate key for orders"
  - name: order_date
    description: "Date of the order"
'''

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        f.write(yaml_content)

    # Run the update function
    result = yaml_manager.update_model_yaml(
        yaml_file,
        "fact_orders",
        "/assets/img/dw/fact/fact_orders_model.html"
    )

    assert result is True

    # Read the updated file
    with open(yaml_file) as f:
        updated = f.read()

    # Verify double quotes are preserved for columns that weren't touched
    assert '"Surrogate key for orders"' in updated, \
        "Double quotes should be preserved for column descriptions"
    assert '"Date of the order"' in updated, \
        "Double quotes should be preserved for all column descriptions"


def test_update_model_yaml_preserve_single_quotes(temp_dir):
    """Test that single quotes in descriptions are preserved."""
    yaml_file = os.path.join(temp_dir, "schema.yml")
    # Write with single quotes explicitly
    with open(yaml_file, "w") as f:
        f.write("""version: 2
models:
- name: fact_orders
  description: 'Order-level fact table'
  columns:
  - name: order_id
    description: 'Surrogate key'
""")

    # Run the update function
    result = yaml_manager.update_model_yaml(
        yaml_file,
        "fact_orders",
        "/assets/img/dw/fact/fact_orders_model.html"
    )

    assert result is True

    # Read the updated file
    with open(yaml_file) as f:
        updated = f.read()

    # Verify single quotes are preserved for columns
    assert "'Surrogate key'" in updated, \
        "Single quotes should be preserved for column descriptions"


def test_update_model_yaml_idempotent_no_changes(temp_dir):
    """Test that running update multiple times with same path is truly idempotent.

    The description should stabilize after the first update and not change on subsequent runs.
    """
    schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table",
                "columns": []
            }
        ]
    }

    yaml_file = os.path.join(temp_dir, "schema.yml")
    with open(yaml_file, "w") as f:
        yaml.dump(schema, f)

    # First update
    yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    with open(yaml_file) as f:
        first_result = f.read()

    # Second update
    yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    with open(yaml_file) as f:
        second_result = f.read()

    # Third update
    yaml_manager.update_model_yaml(
        yaml_file, "fact_orders", "/assets/img/fact/fact_orders_model.html"
    )

    with open(yaml_file) as f:
        third_result = f.read()

    # All results should be identical
    assert first_result == second_result, \
        "Second update should produce identical output to first"
    assert second_result == third_result, \
        "Third update should produce identical output to second"
