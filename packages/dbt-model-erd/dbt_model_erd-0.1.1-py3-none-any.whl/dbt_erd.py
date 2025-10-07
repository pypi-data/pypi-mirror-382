#!/usr/bin/env python
"""dbt-erd: Generate data model diagrams for dbt models

This script reads dbt SQL files, extracts reference relationships, and generates
Mermaid entity-relationship diagrams showing table structures and relationships.

Usage:
    python dbt_erd.py --model-path models/dw/fact [--config config.yml]

Author: Entechlog
Version: 1.0.0
"""

import argparse
import concurrent.futures
import os
import sys

import mermaid_generator as mermaid_gen
import mermaid_renderer
import model_analyzer as analyzer
import utils
import yaml_manager as yaml_mgr

# Import modules
from config import load_config, save_default_config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate data model diagrams for dbt models."
    )
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the fact models directory (e.g., models/dw/fact)",
    )
    parser.add_argument(
        "--project-dir",
        default=os.getcwd(),
        help="dbt project root directory (default: current working directory)",
    )
    parser.add_argument("--config", help="Path to configuration YAML file")
    parser.add_argument(
        "--output-config",
        help="Generate a default config file at the specified path and exit",
    )
    parser.add_argument(
        "--format",
        choices=["mermaid", "html"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel processing regardless of config setting",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output for debugging"
    )
    return parser.parse_args()


def process_model(
    sql_file,
    model_name,
    dimension_tables,
    columns_info,
    config,
    output_format,
    project_dir,
    parent_dir,
    verbose=False,
):
    """Process a single model and generate diagrams for it."""
    try:
        print(f"\nProcessing {model_name}...")
        print(
            "Found {} dimension references: {}".format(
                len(dimension_tables), ", ".join(dimension_tables)
            )
        )

        # Check if columns_info contains dimension tables
        if verbose:
            print("Column info statistics:")
            print(
                f"  Fact table {model_name}: {len(columns_info.get(model_name, []))} columns"
            )
            for dim in dimension_tables:
                print(
                    f"  Dimension table {dim}: {len(columns_info.get(dim, []))} columns"
                )

        # Generate Mermaid diagram content
        diagram_content = mermaid_gen.generate_mermaid_diagram(
            model_name, sql_file, dimension_tables, columns_info, config
        )

        # Create directory structure mirroring the model path
        model_dir = os.path.dirname(sql_file)
        relative_model_path = os.path.relpath(model_dir, project_dir)

        # Determine asset directory based on configuration
        asset_base = config["paths"]["asset_base"]

        if relative_model_path.startswith("models/"):
            asset_dir = os.path.join(
                project_dir, relative_model_path.replace("models/", asset_base + "/", 1)
            )
        else:
            asset_dir = os.path.join(project_dir, asset_base, relative_model_path)

        # Create directories if they don't exist
        utils.ensure_directory_exists(asset_dir)

        # Save the outputs based on configuration
        outputs = mermaid_renderer.save_mermaid_outputs(
            diagram_content, model_name, asset_dir, config
        )

        # Output paths for user
        for fmt, path in outputs.items():
            print(f"Generated {fmt.upper()}: {path}")

        # Get relative asset path for docs (always use HTML for embedding)
        embed_extension = ".html"

        # Get relative asset path for docs
        relative_asset_path = yaml_mgr.get_relative_asset_path(
            project_dir, model_dir, model_name, config, embed_extension
        )

        # Find and update YAML file
        yaml_extension = config["paths"].get("yaml_extension", ".yml")
        yaml_file = analyzer.get_yaml_file_for_model(
            parent_dir, model_name, yaml_extension
        )
        if yaml_file:
            yaml_mgr.update_model_yaml(yaml_file, model_name, relative_asset_path)
        else:
            print(f"Warning: No YAML file found for {model_name}")

        return model_name
    except Exception as e:
        print(f"Error processing model {model_name}: {e}")
        if verbose:
            import traceback

            print(traceback.format_exc())
        return None


def main():
    """Main function to process fact models."""
    args = parse_arguments()

    # Check if we should just generate a default config file
    if args.output_config:
        if save_default_config(args.output_config):
            sys.exit(0)
        else:
            sys.exit(1)

    verbose = args.verbose

    # Load configuration
    config = load_config(args.config)

    project_dir = args.project_dir
    model_path = args.model_path
    output_format = args.format

    # Check if parallel processing should be enabled
    use_parallel = args.parallel or config.get("performance", {}).get("parallel", False)
    max_workers = config.get("performance", {}).get("max_workers", 4)

    if not os.path.isabs(model_path):
        model_path = os.path.join(project_dir, model_path)

    if not os.path.exists(model_path):
        print(f"Error: Model path {model_path} does not exist.")
        return

    # Find all fact model SQL files
    sql_files = utils.find_sql_files(model_path)

    if not sql_files:
        print(f"Warning: No SQL files found in {model_path}")
        return

    # Get column info for all models (including dimension tables)
    print("Collecting column information from YAML files...")
    parent_dir = utils.get_model_directory(model_path, project_dir)

    # We need to look for YAML files in the entire models directory to find dimension table definitions
    models_dir = os.path.join(project_dir, "models")
    if os.path.exists(models_dir):
        print(f"Scanning entire models directory for column information: {models_dir}")
        columns_info = analyzer.get_column_info(
            models_dir, config["paths"]["yaml_extension"]
        )
    else:
        # Fall back to parent_dir if models_dir doesn't exist
        print(f"Scanning parent directory for column information: {parent_dir}")
        columns_info = analyzer.get_column_info(
            parent_dir, config["paths"]["yaml_extension"]
        )

    # Process each SQL file to get model info
    fact_models = []
    for sql_file in sql_files:
        model_name = utils.get_model_name_from_file(sql_file)

        # Check if it's a fact model based on configuration
        if not analyzer.is_fact_table(model_name, sql_file, config):
            continue

        # Extract references
        refs = analyzer.extract_refs_from_sql(sql_file)

        # Filter for dimension tables based on configuration
        dimension_tables = []
        for ref in refs:
            if analyzer.is_dimension_table(ref, config):
                dimension_tables.append(ref)

        if not dimension_tables:
            print(f"Warning: No dimension references found in {model_name}, skipping.")
            continue

        # Add to list of models to process
        fact_models.append((sql_file, model_name, dimension_tables))

    if verbose:
        print("\nDebug information:")
        print(f"Found {len(fact_models)} fact models to process")
        print(f"Column information loaded for {len(columns_info)} models")

    # Process models either in parallel or sequentially
    if use_parallel and len(fact_models) > 1:
        print(
            f"Processing {len(fact_models)} models in parallel with {max_workers} workers..."
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for sql_file, model_name, dimension_tables in fact_models:
                future = executor.submit(
                    process_model,
                    sql_file,
                    model_name,
                    dimension_tables,
                    columns_info,
                    config,
                    output_format,
                    project_dir,
                    parent_dir,
                    verbose,
                )
                futures.append(future)

            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    model_name = future.result()
                    if model_name:
                        print(f"Completed processing {model_name}")
                except Exception as e:
                    print(f"Error in parallel processing: {e}")
                    if verbose:
                        import traceback

                        print(traceback.format_exc())
    else:
        # Process sequentially - this ensures each model is fully processed before moving to the next
        for sql_file, model_name, dimension_tables in fact_models:
            process_model(
                sql_file,
                model_name,
                dimension_tables,
                columns_info,
                config,
                output_format,
                project_dir,
                parent_dir,
                verbose,
            )
            print(f"Completed processing {model_name}")

    print("\nAll models processed.")


if __name__ == "__main__":
    main()
