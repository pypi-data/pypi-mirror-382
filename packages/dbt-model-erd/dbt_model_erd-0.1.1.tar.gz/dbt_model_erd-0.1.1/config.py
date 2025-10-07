#!/usr/bin/env python
"""Configuration management for dbt-erd."""

import os

import yaml

# Default configuration

DEFAULT_CONFIG = {
    # Naming patterns
    "naming": {
        "dimension_patterns": ["dim_", "__dim_", "_dim_", "dw__dim"],
        "fact_patterns": ["fact_", "__fact_", "_fact_", "dw__fact"],
        "dim_pk_patterns": ["_pk", "_key", "_id", "_sk"],
        "fact_pk_patterns": ["_pk", "_key", "_id", "_sk"],
        "fact_fk_patterns": ["_fk", "_id"],
        "table_prefixes": ["dw__", "mart__", "stg__", "obt__"],
    },
    # Visualization settings
    "visualization": {
        "max_dimensions": 20,
        "show_columns": True,
        "column_limit": 75,
    },
    # Mermaid specific settings
    "mermaid": {
        "theme": "default",  # default, forest, dark, neutral
        "direction": "LR",  # TB (top-bottom) or LR (left-right)
        # Output file generation flags
        "outputs": {
            "mmd": True,  # Generate .mmd source file
            "html": True,  # Generate HTML file with interactive diagram
        },
        "interactive": True,  # Enable interactive features in HTML output
        # Styling options
        "style": {
            "fact_table_fill": "#f5f5f5",  # Light gray for fact tables
            "dimension_table_fill": "#e8f4f8",  # Light blue for dimension tables
        },
        # Embedding options for dbt docs
        "embed": {
            "type": "html",  # 'html' only
        },
    },
    # Performance settings
    "performance": {
        "parallel": False,  # Enable parallel processing
        "max_workers": 4,  # Maximum number of worker threads
    },
    # File paths
    "paths": {"asset_base": "assets/img", "yaml_extension": ".yml"},
    # Relationships
    "relationships": {
        "default_type": "many_to_one",  # Default relationship type
        "detect_from_naming": True,
        "show_labels": True,  # Whether to show relationship labels
        "multiple_fk_handling": "first",  # How to handle multiple FK relationships: "first", "all", "none"
        "relationship_types": {
            "many_to_one": {
                "description": "Many-to-One",
                "start_marker": "many",
                "end_marker": "one",
            },
            "one_to_many": {
                "description": "One-to-Many",
                "start_marker": "one",
                "end_marker": "many",
            },
            "many_to_many": {
                "description": "Many-to-Many",
                "start_marker": "many",
                "end_marker": "many",
            },
            "one_to_one": {
                "description": "One-to-One",
                "start_marker": "one",
                "end_marker": "one",
            },
            "zero_one_to_many": {
                "description": "Zero/One-to-Many",
                "start_marker": "zero_one",
                "end_marker": "many",
            },
            "zero_one_to_one": {
                "description": "Zero/One-to-One",
                "start_marker": "zero_one",
                "end_marker": "one",
            },
            "zero_many_to_one": {
                "description": "Zero/Many-to-One",
                "start_marker": "zero_many",
                "end_marker": "one",
            },
        },
    },
}


def load_config(config_path=None):
    """Load configuration from file or use defaults."""
    config = DEFAULT_CONFIG.copy()

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path) as f:
                user_config = yaml.safe_load(f)

            # Merge user config with defaults (recursive merge)
            merge_configs(config, user_config)

            print(f"Using configuration from: {config_path}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration.")
    else:
        if config_path:
            print(f"Config file not found: {config_path}")
            print("Using default configuration.")
        else:
            print("No config file specified. Using default configuration.")

    return config


def merge_configs(base_config, user_config):
    """Recursively merge user config into base config."""
    for key, value in user_config.items():
        if (
            key in base_config
            and isinstance(base_config[key], dict)
            and isinstance(value, dict)
        ):
            merge_configs(base_config[key], value)
        else:
            base_config[key] = value


def save_default_config(output_path):
    """Save the default configuration to a YAML file."""
    try:
        with open(output_path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        print(f"Default configuration saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving default configuration: {e}")
        return False
