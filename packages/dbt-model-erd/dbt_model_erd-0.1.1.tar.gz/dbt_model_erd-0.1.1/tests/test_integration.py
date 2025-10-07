"""End-to-end integration tests for dbt-erd."""

import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as cfg
import dbt_erd


def create_test_dbt_project(project_dir):
    """Create a minimal dbt project structure for testing."""
    # Create directory structure
    models_dir = os.path.join(project_dir, "models")
    fact_dir = os.path.join(models_dir, "fact")
    dim_dir = os.path.join(models_dir, "dim")

    os.makedirs(fact_dir)
    os.makedirs(dim_dir)

    # Create dimension SQL files
    dim_customer_sql = """
WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),

renamed AS (
    SELECT
        id AS customer_id,
        first_name,
        last_name,
        email
    FROM source
)

SELECT * FROM renamed
"""

    with open(os.path.join(dim_dir, "dim_customer.sql"), "w") as f:
        f.write(dim_customer_sql)

    dim_product_sql = """
WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
),

renamed AS (
    SELECT
        id AS product_id,
        name AS product_name,
        category
    FROM source
)

SELECT * FROM renamed
"""

    with open(os.path.join(dim_dir, "dim_product.sql"), "w") as f:
        f.write(dim_product_sql)

    # Create fact SQL file
    fact_orders_sql = """
WITH orders AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

products AS (
    SELECT * FROM {{ ref('dim_product') }}
),

final AS (
    SELECT
        o.id AS order_id,
        o.customer_id,
        o.product_id,
        c.first_name,
        c.last_name,
        p.product_name,
        o.order_date,
        o.amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN products p ON o.product_id = p.product_id
)

SELECT * FROM final
"""

    with open(os.path.join(fact_dir, "fact_orders.sql"), "w") as f:
        f.write(fact_orders_sql)

    # Create dimension YAML schemas
    dim_schema = {
        "version": 2,
        "models": [
            {
                "name": "dim_customer",
                "description": "Customer dimension table",
                "columns": [
                    {
                        "name": "customer_id",
                        "description": "Primary key",
                        "tests": ["unique", "not_null"]
                    },
                    {"name": "first_name", "description": "Customer first name"},
                    {"name": "last_name", "description": "Customer last name"},
                    {"name": "email", "description": "Customer email"}
                ]
            },
            {
                "name": "dim_product",
                "description": "Product dimension table",
                "columns": [
                    {
                        "name": "product_id",
                        "description": "Primary key",
                        "tests": ["unique", "not_null"]
                    },
                    {"name": "product_name", "description": "Product name"},
                    {"name": "category", "description": "Product category"}
                ]
            }
        ]
    }

    with open(os.path.join(dim_dir, "schema.yml"), "w") as f:
        yaml.dump(dim_schema, f, sort_keys=False)

    # Create fact YAML schema
    fact_schema = {
        "version": 2,
        "models": [
            {
                "name": "fact_orders",
                "description": "Order facts table",
                "columns": [
                    {
                        "name": "order_id",
                        "description": "Primary key",
                        "tests": ["unique", "not_null"]
                    },
                    {
                        "name": "customer_id",
                        "description": "Foreign key to customer",
                        "tests": ["not_null"]
                    },
                    {
                        "name": "product_id",
                        "description": "Foreign key to product",
                        "tests": ["not_null"]
                    },
                    {"name": "first_name", "description": "Customer first name"},
                    {"name": "last_name", "description": "Customer last name"},
                    {"name": "product_name", "description": "Product name"},
                    {"name": "order_date", "description": "Order date"},
                    {"name": "amount", "description": "Order amount"}
                ]
            }
        ]
    }

    with open(os.path.join(fact_dir, "schema.yml"), "w") as f:
        yaml.dump(fact_schema, f, sort_keys=False)

    return models_dir, fact_dir, dim_dir


def test_end_to_end_diagram_generation():
    """Test the complete flow of generating ERD diagrams."""
    with tempfile.TemporaryDirectory() as project_dir:
        # Create test dbt project
        models_dir, fact_dir, dim_dir = create_test_dbt_project(project_dir)

        # Load default config
        config = cfg.load_config()

        # Override paths for testing
        config["paths"]["asset_base"] = "assets/img"

        # Get column info
        import model_analyzer
        columns_info = model_analyzer.get_column_info(models_dir)

        # Verify columns were loaded
        assert "fact_orders" in columns_info
        assert "dim_customer" in columns_info
        assert "dim_product" in columns_info

        # Extract refs from fact_orders
        fact_orders_file = os.path.join(fact_dir, "fact_orders.sql")
        refs = model_analyzer.extract_refs_from_sql(fact_orders_file)

        # Should find both dimension refs
        assert len(refs) == 2
        assert "dim_customer" in refs
        assert "dim_product" in refs

        # Filter for dimension tables
        dimension_tables = [
            ref for ref in refs
            if model_analyzer.is_dimension_table(ref, config)
        ]
        assert len(dimension_tables) == 2

        # Generate Mermaid diagram
        import mermaid_generator
        diagram_content = mermaid_generator.generate_mermaid_diagram(
            "fact_orders",
            fact_orders_file,
            dimension_tables,
            columns_info,
            config
        )

        # Verify diagram content
        assert "erDiagram" in diagram_content
        assert "fact_orders" in diagram_content
        assert "dim_customer" in diagram_content
        assert "dim_product" in diagram_content

        # Verify relationships are present
        assert "||--o{" in diagram_content or "}o--||" in diagram_content

        # Save outputs
        import mermaid_renderer
        asset_dir = os.path.join(project_dir, "assets", "img", "fact")
        os.makedirs(asset_dir, exist_ok=True)

        outputs = mermaid_renderer.save_mermaid_outputs(
            diagram_content, "fact_orders", asset_dir, config
        )

        # Verify outputs were created
        assert "mmd" in outputs
        assert "html" in outputs
        assert os.path.exists(outputs["mmd"])
        assert os.path.exists(outputs["html"])

        # Verify HTML content
        with open(outputs["html"]) as f:
            html_content = f.read()
            assert "<html>" in html_content
            assert "mermaid" in html_content.lower()
            assert "erDiagram" in html_content

        # Update YAML
        import yaml_manager
        yaml_file = os.path.join(fact_dir, "schema.yml")
        relative_path = "/assets/img/fact/fact_orders_model.html"

        result = yaml_manager.update_model_yaml(yaml_file, "fact_orders", relative_path)
        assert result is True

        # Verify YAML was updated
        with open(yaml_file) as f:
            updated_schema = yaml.safe_load(f)

        fact_model = updated_schema["models"][0]
        assert fact_model["name"] == "fact_orders"
        assert "## Data Model Diagram" in fact_model["description"]
        assert relative_path in fact_model["description"]


def test_multiple_fact_tables():
    """Test processing multiple fact tables in one run."""
    with tempfile.TemporaryDirectory() as project_dir:
        # Create basic structure
        models_dir, fact_dir, dim_dir = create_test_dbt_project(project_dir)

        # Add a second fact table
        fact_sales_sql = """
WITH sales AS (
    SELECT * FROM {{ source('raw', 'sales') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

final AS (
    SELECT
        s.id AS sale_id,
        s.customer_id,
        c.first_name,
        s.sale_date,
        s.total
    FROM sales s
    LEFT JOIN customers c ON s.customer_id = c.customer_id
)

SELECT * FROM final
"""

        with open(os.path.join(fact_dir, "fact_sales.sql"), "w") as f:
            f.write(fact_sales_sql)

        # Add YAML for second fact
        with open(os.path.join(fact_dir, "schema.yml")) as f:
            fact_schema = yaml.safe_load(f)

        fact_schema["models"].append({
            "name": "fact_sales",
            "description": "Sales facts table",
            "columns": [
                {"name": "sale_id", "tests": ["unique", "not_null"]},
                {"name": "customer_id", "tests": ["not_null"]},
                {"name": "first_name"},
                {"name": "sale_date"},
                {"name": "total"}
            ]
        })

        with open(os.path.join(fact_dir, "schema.yml"), "w") as f:
            yaml.dump(fact_schema, f, sort_keys=False)

        # Process models
        import model_analyzer
        import utils

        sql_files = utils.find_sql_files(fact_dir)
        assert len(sql_files) == 2

        config = cfg.load_config()
        _ = model_analyzer.get_column_info(models_dir)

        fact_models = []
        for sql_file in sql_files:
            model_name = utils.get_model_name_from_file(sql_file)
            if model_analyzer.is_fact_table(model_name, sql_file, config):
                refs = model_analyzer.extract_refs_from_sql(sql_file)
                dimension_tables = [
                    ref for ref in refs
                    if model_analyzer.is_dimension_table(ref, config)
                ]
                if dimension_tables:
                    fact_models.append((sql_file, model_name, dimension_tables))

        # Should find both fact models
        assert len(fact_models) == 2
        model_names = [m[1] for m in fact_models]
        assert "fact_orders" in model_names
        assert "fact_sales" in model_names


def test_no_dimension_references():
    """Test handling of fact table with no dimension references."""
    with tempfile.TemporaryDirectory() as project_dir:
        # Create simple fact without refs
        models_dir = os.path.join(project_dir, "models")
        fact_dir = os.path.join(models_dir, "fact")
        os.makedirs(fact_dir)

        fact_sql = "SELECT * FROM {{ source('raw', 'data') }}"
        with open(os.path.join(fact_dir, "fact_simple.sql"), "w") as f:
            f.write(fact_sql)

        fact_schema = {
            "version": 2,
            "models": [
                {
                    "name": "fact_simple",
                    "description": "Simple fact",
                    "columns": [{"name": "id"}]
                }
            ]
        }

        with open(os.path.join(fact_dir, "schema.yml"), "w") as f:
            yaml.dump(fact_schema, f)

        # Process
        import model_analyzer
        import utils

        config = cfg.load_config()
        sql_files = utils.find_sql_files(fact_dir)

        for sql_file in sql_files:
            model_name = utils.get_model_name_from_file(sql_file)
            if model_analyzer.is_fact_table(model_name, sql_file, config):
                refs = model_analyzer.extract_refs_from_sql(sql_file)
                # Should find no refs
                assert len(refs) == 0
