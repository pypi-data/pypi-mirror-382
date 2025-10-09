# Copyright (C) 2025 Embedl AB

"""Tests for TuningConfig class."""

import pytest
import yaml

from embedl_hub.core.config import default_configs
from embedl_hub.core.tuning.tuning_config import TuningConfig


@pytest.fixture
def sample_yaml(tmp_path):
    """Fixture to create a sample YAML file for testing."""
    data = {
        "model_id": "default-model",
        "num_classes": 2,
        "data_path": "/mnt/data/train",
        "batch_size": 16,
        "epochs": 3,
    }
    path = tmp_path / "tune_default.yaml"
    path.write_text(yaml.dump(data))
    return path


def test_from_yaml_loads_all_fields(sample_yaml):
    """Test that TuningConfig can load a YAML file."""
    cfg = TuningConfig.from_yaml(sample_yaml)
    assert cfg.model_id == "default-model"
    assert cfg.num_classes == 2
    assert cfg.data_path == "/mnt/data/train"
    assert cfg.batch_size == 16
    assert cfg.epochs == 3


def test_merge_yaml_no_overrides(sample_yaml):
    """Test that merging with no overrides returns the same config."""
    cfg = TuningConfig.from_yaml(sample_yaml)
    merged = cfg.merge_yaml(other=None, cli_flags={})
    assert merged == cfg


def test_merge_yaml_file_override(tmp_path, sample_yaml):
    """Test that merging with a file override works correctly."""
    # Create an override YAML with some changed values
    override = {"num_classes": 5, "batch_size": 8}
    override_path = tmp_path / "override.yaml"
    override_path.write_text(yaml.dump(override))
    cfg = TuningConfig.from_yaml(sample_yaml)
    merged = cfg.merge_yaml(other=override_path, cli_flags={})
    # fields from override file should take precedence
    assert merged.num_classes == 5
    assert merged.batch_size == 8
    # and other fields remain as in the default
    assert merged.model_id == "default-model"
    assert merged.epochs == 3


def test_merge_yaml_cli_overrides(sample_yaml):
    """Test that merging with CLI overrides works correctly."""
    cfg = TuningConfig.from_yaml(sample_yaml)
    cli = {
        "model_id": "cli-model",
        "epochs": 10,
        # leave num_classes unset to pick up from file
    }
    merged = cfg.merge_yaml(other=None, **cli)
    assert merged.model_id == "cli-model"
    assert merged.epochs == 10
    assert merged.num_classes == 2  # from original YAML


def test_non_complete_default_configs(monkeypatch, tmp_path):
    """Test that TuningConfig can load a YAML file with missing fields."""
    # 1) create a fake "default" YAML, where `epochs` is missing
    data = {
        "model_id": "default-from-global",
        "num_classes": 7,
        "data_path": "/tmp/data",
        "batch_size": 99,
    }
    default_file = tmp_path / "fake_default.yaml"
    default_file.write_text(yaml.dump(data))

    # 2) monkey-patch the global default_configs to point at it
    monkeypatch.setitem(default_configs, "tune", default_file)

    # 3) load via from_yaml(default_configs["tune"])
    cfg = TuningConfig.from_yaml(default_configs["tune"])

    # 4) assert every field matches what we wrote
    assert cfg.model_id == "default-from-global"
    assert cfg.num_classes == 7
    assert cfg.data_path == "/tmp/data"
    assert cfg.batch_size == 99


if __name__ == "__main__":
    pytest.main([__file__])
