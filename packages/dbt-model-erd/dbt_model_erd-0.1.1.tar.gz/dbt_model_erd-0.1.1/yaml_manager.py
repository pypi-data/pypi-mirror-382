#!/usr/bin/env python
"""YAML operations for dbt-erd."""

import os

from ruamel.yaml import YAML


def update_model_yaml(yaml_file, model_name, relative_path):
    """Update model YAML to reference the diagram.

    Args:
        yaml_file: Path to the YAML file
        model_name: Name of the model to update
        relative_path: Relative path to the diagram file

    Returns:
        True if the update was successful, False otherwise
    """
    if not os.path.exists(yaml_file):
        print(f"Warning: YAML file {yaml_file} not found, skipping update.")
        return False

    try:
        yaml_handler = YAML()
        yaml_handler.preserve_quotes = True
        yaml_handler.width = 4096  # Prevent line wrapping

        with open(yaml_file) as f:
            try:
                config = yaml_handler.load(f)
            except Exception as e:
                print(f"Error parsing YAML file {yaml_file}: {e}")
                return False

        # Find the model in the YAML
        modified = False
        if not config or "models" not in config:
            print(f"Warning: No models section found in {yaml_file}")
            return False

        for model in config.get("models", []):
            if model.get("name") == model_name:
                desc = model.get("description", "")

                # We only use HTML diagrams
                diagram_section = "\n\n## Data Model Diagram\n\n"
                diagram_section += f"[View interactive diagram]({relative_path})"

                # Update the description
                if "## Data Model Diagram" in desc:
                    # Replace existing diagram section
                    parts = desc.split("## Data Model Diagram")
                    before_diagram = parts[0].rstrip()  # Remove trailing whitespace/newlines
                    after_diagram = ""
                    if len(parts) > 1 and "##" in parts[1]:
                        after_section = parts[1].split("##", 1)
                        after_diagram = "\n\n##" + after_section[1].rstrip()

                    model["description"] = before_diagram + diagram_section
                    if after_diagram:
                        model["description"] += after_diagram
                else:
                    # Add new diagram section
                    # Remove trailing whitespace from existing description
                    desc = desc.rstrip() if desc else ""
                    model["description"] = desc + diagram_section

                modified = True
                break

        if not modified:
            print(f"Warning: Model {model_name} not found in {yaml_file}")
            return False

        # Write the updated YAML
        with open(yaml_file, "w") as f:
            yaml_handler.dump(config, f)

        print(f"Updated model description in {yaml_file}")
        return True

    except Exception as e:
        print(f"Error updating YAML file {yaml_file}: {e}")
        return False


def get_relative_asset_path(
    project_dir, model_path, model_name, config, file_extension=None
):
    """Create the relative asset path that mirrors the model path structure.

    Args:
        project_dir: Path to the dbt project root
        model_path: Path to the model file
        model_name: Name of the model
        config: Configuration dictionary
        file_extension: Optional file extension to override default

    Returns:
        Relative path to the asset file
    """
    # Get relative path from project_dir to model_path
    model_rel_path = os.path.relpath(model_path, project_dir)

    # Normalize path separators to forward slashes for cross-platform compatibility
    model_rel_path = model_rel_path.replace(os.sep, "/")

    # Get the asset base path from config
    asset_base = config["paths"]["asset_base"]

    # If file_extension not provided, default to HTML
    if not file_extension:
        file_extension = ".html"

    # Replace "models/" with asset base path
    if model_rel_path.startswith("models/"):
        asset_rel_path = model_rel_path.replace("models/", asset_base + "/", 1)
    else:
        asset_rel_path = asset_base + "/" + model_rel_path

    # Return relative path for docs reference (from project root)
    return "/{}/{}".format(asset_rel_path, model_name + "_model" + file_extension)
