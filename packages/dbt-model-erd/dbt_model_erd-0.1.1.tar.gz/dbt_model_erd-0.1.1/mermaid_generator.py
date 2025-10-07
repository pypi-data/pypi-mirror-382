#!/usr/bin/env python
"""Mermaid diagram generation for dbt-erd."""

import model_analyzer as analyzer


def generate_mermaid_diagram(
    fact_table, fact_file, dimension_tables, columns_info, config
):
    """Generate a Mermaid entity-relationship diagram showing table structures and relationships.

    Args:
        fact_table: Name of the fact table
        fact_file: Path to the fact table file
        dimension_tables: List of dimension table names
        columns_info: Dictionary mapping model names to their column information
        config: Configuration dictionary

    Returns:
        Mermaid diagram content as a string
    """
    # Get column information for fact table
    fact_columns = columns_info.get(fact_table, [])

    # Debug - print column info
    print(f"Fact table {fact_table} has {len(fact_columns)} columns.")

    # Determine max columns to show
    column_limit = config.get("visualization", {}).get("column_limit", 20)
    show_columns = config.get("visualization", {}).get("show_columns", True)
    max_dimensions = config.get("visualization", {}).get("max_dimensions", 10)

    # Find primary key for fact table
    fact_pk = analyzer.find_primary_key(fact_columns, config, fact_table, is_fact=True)

    # Identify foreign keys in fact table
    foreign_keys = []
    fk_patterns = config["naming"]["fact_fk_patterns"]
    for col in fact_columns:
        col_name = col["name"].lower()
        for pattern in fk_patterns:
            if pattern in col_name and col_name != fact_pk.lower():
                foreign_keys.append(col["name"])
                break
        desc = col.get("description", "").lower()
        if "foreign key" in desc or "fk" in desc:
            if col["name"] not in foreign_keys:
                foreign_keys.append(col["name"])

    # Start building Mermaid diagram
    mermaid = "erDiagram\n"

    # Add fact table
    mermaid += generate_table_entity(
        fact_table, fact_columns, fact_pk, foreign_keys, show_columns, column_limit
    )

    # Add dimension tables (limited by max_dimensions)
    included_dims = (
        dimension_tables[:max_dimensions] if max_dimensions > 0 else dimension_tables
    )

    for dim in included_dims:
        # Get dimension table columns
        dim_columns = columns_info.get(dim, [])

        # Debug - print dimension column info
        print(f"Dimension table {dim} has {len(dim_columns)} columns.")

        dim_pk = analyzer.find_primary_key(dim_columns, config, dim)

        mermaid += generate_table_entity(
            dim, dim_columns, dim_pk, [], show_columns, column_limit
        )

        # Find foreign keys for relationship (there might be multiple)
        entity_name = analyzer.extract_entity_name(dim, config)

        # Get all foreign keys that might reference this dimension
        all_fk_names = analyzer.find_all_foreign_keys_for_dimension(
            fact_columns, dim, entity_name, config
        )

        # Determine how to handle multiple FKs
        fk_handling = config["relationships"].get("multiple_fk_handling", "first")

        if not all_fk_names:
            # No foreign keys found, generate one with default naming
            default_fk = f"{entity_name.lower()}_id"
            relationship_type = analyzer.detect_relationship_type(
                fact_columns, default_fk, dim, config
            )
            mermaid += generate_relationship(
                dim, fact_table, default_fk, relationship_type, config
            )
        elif fk_handling == "first" or len(all_fk_names) == 1:
            # Use only the first FK or there's only one anyway
            fk_name = all_fk_names[0]
            relationship_type = analyzer.detect_relationship_type(
                fact_columns, fk_name, dim, config
            )
            mermaid += generate_relationship(
                dim, fact_table, fk_name, relationship_type, config
            )
        elif fk_handling == "all":
            # Show all FKs as a comma-separated list
            fk_names_combined = ", ".join(all_fk_names)
            relationship_type = analyzer.detect_relationship_type(
                fact_columns, all_fk_names[0], dim, config
            )
            mermaid += generate_relationship(
                dim, fact_table, fk_names_combined, relationship_type, config
            )
        else:  # 'none' or any other value
            # Don't show any labels
            relationship_type = analyzer.detect_relationship_type(
                fact_columns, all_fk_names[0], dim, config
            )
            mermaid += generate_relationship(
                dim, fact_table, None, relationship_type, config
            )

    # If there are more dimensions than we're showing, add a note
    if max_dimensions > 0 and len(dimension_tables) > max_dimensions:
        remaining = len(dimension_tables) - max_dimensions
        mermaid += f'    note "{remaining} more dimension tables not shown (configured max_dimensions: {max_dimensions})"\n'

    return mermaid


def generate_table_entity(
    table_name, columns, pk_name, fk_names, show_columns, column_limit
):
    """Generate Mermaid entity definition for a table.

    Args:
        table_name: Name of the table
        columns: List of column dictionaries
        pk_name: Name of the primary key column
        fk_names: List of foreign key column names
        show_columns: Whether to show columns
        column_limit: Maximum number of columns to show

    Returns:
        Mermaid entity definition as a string
    """
    result = f"    {table_name} {{\n"

    if show_columns and columns:
        # Apply the column limit (if provided)
        if column_limit and column_limit > 0 and len(columns) > column_limit:
            display_columns = columns[:column_limit]
            # Note: We don't show the "remaining columns" text anymore since it's not supported
            # Instead, we'll show the limited number of columns without a note
        else:
            display_columns = columns

        for col in display_columns:
            col_name = col["name"]
            # Set appropriate type
            col_type = get_column_type(col)

            # Add indicators for PK and FK
            if col_name.lower() == pk_name.lower():
                result += f"        {col_type} {col_name} PK\n"
            elif col_name in fk_names:
                result += f"        {col_type} {col_name} FK\n"
            else:
                result += f"        {col_type} {col_name}\n"
    else:
        # If not showing columns, at least show the primary key
        result += f"        string {pk_name} PK\n"

    result += "    }\n\n"
    return result


def get_column_type(column):
    """Infer column type from name or description.
    
    This is a simplified type inference system with the following limitations:
    - Only detects common naming patterns
    - May misclassify columns with ambiguous names
    - Doesn't handle complex types (arrays, JSON, etc.)
    
    For production use, consider supplementing with database metadata
    or allowing manual type overrides.
    
    Args:
        column: Column dictionary with name and optional description
        
    Returns:
        Inferred data type as a string: date, float, int, boolean, or string
    """
    name = column["name"].lower()
    desc = column.get("description", "").lower()
    
    # Boolean checks (highest precedence)
    if (name.startswith(("is_", "has_", "can_", "should_", "does_")) or 
        name.startswith(("is", "has", "can", "should", "does")) or
        "flag" in name or "enabled" in name or "active" in name):
        return "boolean"
        
    # Date/time checks
    if ("date" in name or "time" in name or "dt_" in name or 
        name.endswith(("_at", "_date", "_time")) or 
        name.startswith(("date", "time", "dt")) or
        "timestamp" in name or "created" in name or "updated" in name):
        return "date"
        
    # Numeric checks - float
    if ("amount" in name or "price" in name or "cost" in name or 
        "revenue" in name or "fee" in name or "rate" in name or
        "total" in name or "avg" in name or "average" in name or
        "pct" in name or "percent" in name or "ratio" in name or
        name.endswith(("_amt", "_price", "_cost", "_pct", "_rate")) or
        "balance" in name or "sum" in name):
        return "float"
        
    # Numeric checks - integer
    if ("count" in name or "num" in name or "_qty" in name or 
        name.endswith("_id") or "_id_" in name or 
        name.endswith(("_count", "_num", "_qty", "_age", "_year")) or
        "position" in name or "rank" in name or "order" in name):
        return "int"
    
    # Description-based checks
    if desc:
        # Boolean
        if ("boolean" in desc or "bool" in desc or "flag" in desc or 
            "yes/no" in desc or "yes or no" in desc or 
            "true/false" in desc or "true or false" in desc):
            return "boolean"
            
        # Date
        if ("date" in desc or "time" in desc or "timestamp" in desc or
            "when" in desc and ("created" in desc or "updated" in desc or "occurred" in desc)):
            return "date"
            
        # Float
        if ("decimal" in desc or "numeric" in desc or "float" in desc or
            "double" in desc or "real" in desc or
            "currency" in desc or "money" in desc or "dollar" in desc or
            "percentage" in desc or "ratio" in desc or "proportion" in desc):
            return "float"
            
        # Integer
        if ("integer" in desc or "number" in desc or "int" in desc or
            "count" in desc or "quantity" in desc or "how many" in desc):
            return "int"
    
    # Default to string
    return "string"


def generate_relationship(dim_table, fact_table, fk_name, relationship_type, config):
    """Generate Mermaid relationship between tables.

    Args:
        dim_table: Name of the dimension table
        fact_table: Name of the fact table
        fk_name: Name of the foreign key column(s) or None if no label
        relationship_type: Type of relationship
        config: Configuration dictionary

    Returns:
        Mermaid relationship definition as a string
    """
    # Map relationship type to Mermaid notation
    # Mermaid uses: 1, 0, 1+, 0+ for cardinality
    rel_mapping = {
        "many_to_one": "||--o{",
        "one_to_many": "}o--||",
        "many_to_many": "}o--o{",
        "one_to_one": "||--||",
        "zero_one_to_many": "|o--o{",
        "zero_one_to_one": "|o--||",
        "zero_many_to_one": "||--o|",
    }

    rel_symbol = rel_mapping.get(relationship_type, "||--o{")  # Default to many-to-one

    # Check if we should show relationship labels
    show_labels = config["relationships"].get("show_labels", True)

    # Create relationship
    if show_labels and fk_name:
        return f'    {dim_table} {rel_symbol} {fact_table} : "{fk_name}"\n'
    else:
        return f"    {dim_table} {rel_symbol} {fact_table}\n"
