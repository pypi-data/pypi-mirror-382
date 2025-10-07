"""Tests for config.py functions."""

import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def test_load_config_default():
    """Test loading default configuration."""
    # Test without config file
    cfg = config.load_config()
    assert isinstance(cfg, dict)
    assert "naming" in cfg
    assert "visualization" in cfg
    assert "mermaid" in cfg
    
    # Test with non-existent config file
    cfg = config.load_config("/path/to/nonexistent/config.yml")
    assert isinstance(cfg, dict)
    assert "naming" in cfg


def test_load_config_custom(temp_dir):
    """Test loading custom configuration."""
    # Create a custom config file
    custom_config = {
        "naming": {
            "dimension_patterns": ["dimension_", "dim_"],
            "fact_patterns": ["fact_", "fct_"]
        },
        "mermaid": {
            "theme": "forest"
        }
    }
    
    config_path = os.path.join(temp_dir, "custom_config.yml")
    with open(config_path, "w") as f:
        yaml.dump(custom_config, f)
    
    # Load the custom config
    cfg = config.load_config(config_path)
    
    # Custom settings should be applied
    assert cfg["naming"]["dimension_patterns"] == ["dimension_", "dim_"]
    assert cfg["naming"]["fact_patterns"] == ["fact_", "fct_"]
    assert cfg["mermaid"]["theme"] == "forest"
    
    # Default settings should still be present for items not in custom config
    assert "visualization" in cfg
    assert "paths" in cfg


def test_merge_configs():
    """Test merging configurations."""
    base_config = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3
        },
        "e": [4, 5]
    }
    
    user_config = {
        "a": 10,
        "b": {
            "c": 20
        },
        "f": 30
    }
    
    # Merge user config into base config
    config.merge_configs(base_config, user_config)
    
    # Check that values were merged correctly
    assert base_config["a"] == 10  # Overwritten
    assert base_config["b"]["c"] == 20  # Nested overwritten
    assert base_config["b"]["d"] == 3  # Nested preserved
    assert base_config["e"] == [4, 5]  # Preserved
    assert base_config["f"] == 30  # Added


def test_save_default_config(temp_dir):
    """Test saving default configuration to a file."""
    output_path = os.path.join(temp_dir, "default_config.yml")
    
    # Save default config
    result = config.save_default_config(output_path)
    
    # Should return True on success
    assert result is True
    
    # File should exist
    assert os.path.exists(output_path)
    
    # Should be able to load the saved config
    with open(output_path) as f:
        saved_config = yaml.safe_load(f)
    
    # Should match the default config
    assert saved_config == config.DEFAULT_CONFIG
