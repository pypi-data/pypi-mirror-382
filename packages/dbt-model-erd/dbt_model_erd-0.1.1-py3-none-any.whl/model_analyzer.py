#!/usr/bin/env python
"""DBT model analysis for dbt-erd."""

import os
import re

import yaml


def extract_refs_from_sql(sql_file):
    """Extract {{ ref('...') }} statements from a SQL file.

    Args:
        sql_file: Path to the SQL file

    Returns:
        List of reference names
    """
    with open(sql_file) as f:
        content = f.read()

    # Find all ref statements
    refs = re.findall(r"{{\s*ref\s*\(\s*['\"](.*?)['\"]\s*\)\s*}}", content)
    return list(set(refs))  # Deduplicate refs


def get_column_info(model_path, yaml_extension=".yml"):
    """Scan YAML files to collect column information for all models.
    This function loads ALL columns for each model from its YAML definition.

    Args:
        model_path: Path to the dbt models directory
        yaml_extension: File extension for YAML files

    Returns:
        Dictionary mapping model names to their column information
    """
    model_columns = {}

    # Recursively find all YAML files
    yaml_files = []
    for root, _dirs, files in os.walk(model_path):
        for file in files:
            if file.endswith(yaml_extension):
                yaml_files.append(os.path.join(root, file))

    print(f"Found {len(yaml_files)} YAML files to scan for column information")

    for yaml_file in yaml_files:
        try:
            with open(yaml_file) as f:
                config = yaml.safe_load(f)

            if not config or "models" not in config:
                continue

            for model in config.get("models", []):
                model_name = model.get("name")
                if model_name and "columns" in model:
                    model_columns[model_name] = model.get("columns", [])
                    print(
                        f"Loaded {len(model_columns[model_name])} columns for model {model_name} from {yaml_file}"
                    )
        except Exception as e:
            print(f"Warning: Error parsing {yaml_file}: {e}")

    # Print summary of loaded columns
    print(f"Loaded column information for {len(model_columns)} models")
    for model_name, columns in model_columns.items():
        print(f"  - {model_name}: {len(columns)} columns")

    return model_columns


def get_yaml_file_for_model(model_path, model_name, yaml_extension=".yml"):
    """Find the YAML file containing the model definition.

    Args:
        model_path: Path to the dbt models directory
        model_name: Name of the model to find
        yaml_extension: File extension for YAML files

    Returns:
        Path to the YAML file containing the model, or None if not found
    """
    # Recursively find all YAML files
    yaml_files = []
    for root, _dirs, files in os.walk(model_path):
        for file in files:
            if file.endswith(yaml_extension):
                yaml_files.append(os.path.join(root, file))

    for yaml_file in yaml_files:
        try:
            with open(yaml_file) as f:
                config = yaml.safe_load(f)

            if not config or "models" not in config:
                continue

            for model in config.get("models", []):
                if model.get("name") == model_name:
                    return yaml_file
        except Exception:
            continue

    return None


def is_fact_table(model_name, file_path, config):
    """Determine if a model is a fact table based on naming patterns.

    Args:
        model_name: Name of the model
        file_path: Path to the model file
        config: Configuration dictionary

    Returns:
        True if the model is a fact table, False otherwise
    """
    fact_patterns = config["naming"]["fact_patterns"]

    # Check if any fact pattern is in the model name
    for pattern in fact_patterns:
        if pattern in model_name.lower():
            return True

    # Check if 'fact' is in the file path
    if "fact" in file_path.lower():
        return True

    return False


def is_dimension_table(model_name, config):
    """Determine if a model is a dimension table based on naming patterns.

    Args:
        model_name: Name of the model
        config: Configuration dictionary

    Returns:
        True if the model is a dimension table, False otherwise
    """
    dim_patterns = config["naming"]["dimension_patterns"]

    # Check if any dimension pattern is in the model name
    for pattern in dim_patterns:
        if pattern in model_name.lower():
            return True

    return False


def extract_entity_name(table_name, config):
    """Extract the entity name from a table name based on configuration.

    Args:
        table_name: Name of the table
        config: Configuration dictionary

    Returns:
        Extracted entity name
    """
    # Remove prefixes
    name = table_name
    for prefix in config["naming"]["table_prefixes"]:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break

    # Remove dimension prefixes
    for pattern in config["naming"]["dimension_patterns"]:
        if pattern in name:
            parts = name.split(pattern, 1)
            if len(parts) > 1:
                return parts[1]

    # Remove fact prefixes
    for pattern in config["naming"]["fact_patterns"]:
        if pattern in name:
            parts = name.split(pattern, 1)
            if len(parts) > 1:
                return parts[1]

    # If all else fails, just return the name
    return name


def detect_relationship_type(fact_columns, fk_name, dim_table, config):
    """Detect relationship type based on column information and naming patterns.

    Args:
        fact_columns: List of fact table column dictionaries
        fk_name: Name of the foreign key column
        dim_table: Name of the dimension table
        config: Configuration dictionary

    Returns:
        Relationship type string
    """
    # Default type from configuration
    default_type = config["relationships"]["default_type"]

    # If detecting from naming is disabled, just return the default
    if not config["relationships"]["detect_from_naming"]:
        return default_type

    # Check for test definitions
    for col in fact_columns:
        if col.get("name") == fk_name and col.get("tests"):
            tests = col.get("tests", [])
            has_unique = any(
                test == "unique" or (isinstance(test, dict) and "unique" in test)
                for test in tests
            )

            if has_unique:
                return "one_to_one"

            has_not_null = any(
                test == "not_null" or (isinstance(test, dict) and "not_null" in test)
                for test in tests
            )

            if not has_not_null:
                return "zero_one_to_many"

    # Checks based on naming patterns
    if fk_name and ("many" in fk_name.lower() or fk_name.endswith("s_id")):
        return "many_to_many"

    # Default case
    return default_type


def find_primary_key(columns, config, table_name=None, is_fact=False):
    """Find the primary key column in a list of column dictionaries.

    Args:
        columns: List of column dictionaries
        config: Configuration dictionary
        table_name: Name of the table (optional)
        is_fact: Whether this is a fact table (optional)

    Returns:
        Name of the primary key column, or None if not found
    """
    # Choose appropriate PK patterns based on table type
    pk_patterns = (
        config["naming"]["fact_pk_patterns"]
        if is_fact
        else config["naming"]["dim_pk_patterns"]
    )

    # First check for primary key based on tests
    for col in columns:
        if col.get("tests"):
            for test in col.get("tests", []):
                if (
                    test == "unique"
                    or test == "primary_key"
                    or (
                        isinstance(test, dict)
                        and ("unique" in test or "primary_key" in test)
                    )
                ):
                    return col["name"]

    # If not found, try to identify primary key by naming pattern
    for col in columns:
        col_name = col["name"].lower()
        for pattern in pk_patterns:
            if pattern in col_name:
                return col["name"]

    # As a last resort, use the first column
    if columns:
        return columns[0]["name"]

    # If no columns defined, use a generic name
    return "id"


def find_foreign_key_for_dimension(fact_columns, dim_table, entity_name, config):
    """Find the most likely foreign key column that references a dimension table.

    Args:
        fact_columns: List of fact table column dictionaries
        dim_table: Name of the dimension table
        entity_name: Extracted entity name from the dimension table
        config: Configuration dictionary

    Returns:
        Name of the foreign key column, or a generated name if not found
    """
    all_fks = find_all_foreign_keys_for_dimension(
        fact_columns, dim_table, entity_name, config
    )
    if all_fks:
        return all_fks[0]  # Return the first (most likely) match

    # As a last resort, generate a name
    entity_parts = entity_name.split("_")
    core_entity = entity_parts[-1] if entity_parts else entity_name
    return f"{core_entity}_id"


def find_all_foreign_keys_for_dimension(fact_columns, dim_table, entity_name, config):
    """Find all possible foreign key columns that might reference a dimension table.

    Args:
        fact_columns: List of fact table column dictionaries
        dim_table: Name of the dimension table
        entity_name: Extracted entity name from the dimension table
        config: Configuration dictionary

    Returns:
        List of foreign key column names
    """
    matching_fks = []

    # Special handling for common patterns
    entity_parts = entity_name.split("_")
    core_entity = entity_parts[-1] if entity_parts else entity_name

    # Look for columns that contain the entity name and end with _id
    for col in fact_columns:
        col_name = col["name"].lower()
        if core_entity.lower() in col_name and col_name.endswith("_id"):
            matching_fks.append(col["name"])

    # Look through descriptions for matches
    for col in fact_columns:
        desc = col.get("description", "").lower()
        if (
            core_entity.lower() in desc or entity_name.lower() in desc
        ) and "foreign key" in desc:
            if col["name"] not in matching_fks:
                matching_fks.append(col["name"])

    # If we found exact matches, return them
    if matching_fks:
        return matching_fks

    # Otherwise, try to find potential matches based on foreign key patterns
    potential_fks = []
    fk_patterns = config["naming"]["fact_fk_patterns"]

    for col in fact_columns:
        col_name = col["name"].lower()
        for pattern in fk_patterns:
            if pattern in col_name:
                potential_fks.append(col["name"])
                break

    # If we have potential foreign keys, filter for likely matches with this dimension
    if potential_fks:
        # Try to find matches with the entity name
        entity_matches = [
            fk for fk in potential_fks if core_entity.lower() in fk.lower()
        ]

        if entity_matches:
            return entity_matches
        else:
            return potential_fks  # Return all potential FKs if no entity matches

    # No matches found
    return []
