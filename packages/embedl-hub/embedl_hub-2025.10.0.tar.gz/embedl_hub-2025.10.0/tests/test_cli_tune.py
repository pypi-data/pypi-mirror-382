# Copyright (C) 2025 Embedl AB

"""Test the CLI for tuning models using the Embedl Hub SDK."""

import pytest
import yaml
from typer.testing import CliRunner

from embedl_hub.cli.tune import tune_cli


def test_tune_cli_uses_default_config():
    """
    Test the CLI with default configuration.

    The test should fail due to lacking config settings.
    """

    runner = CliRunner()
    result = runner.invoke(tune_cli)
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)


def test_tune_cli_overrides_with_flags(monkeypatch):
    """Test the CLI with command-line flags to override default configuration."""

    captured = {}

    # pylint: disable-next=unused-argument
    def fake_tune_model(config, project_name, experiment_name):
        """Fake tune_model function to capture the config."""
        captured["cfg"] = config

    monkeypatch.setattr(
        "embedl_hub.core.tuning.tuner.tune_model", fake_tune_model
    )
    monkeypatch.setattr('embedl_hub.cli.utils.assert_api_config', lambda: None)
    monkeypatch.setattr(
        "embedl_hub.core.context.read_embedl_hub_context",
        lambda: {
            "project_name": "test_project",
            "experiment_name": "test_experiment",
        },
    )

    runner = CliRunner()
    args = [
        "--model_id",
        "my-model",
        "--num-classes",
        "10",
        "--data",
        "/other/data",
        "--batch-size",
        "64",
        "--epochs",
        "7",
    ]
    result = runner.invoke(tune_cli, args)
    assert result.exit_code == 0

    cfg = captured["cfg"]
    assert cfg.model_id == "my-model"
    assert cfg.num_classes == 10
    assert cfg.data_path == "/other/data"
    assert cfg.batch_size == 64
    assert cfg.epochs == 7


def test_tune_cli_with_custom_config_file(tmp_path, monkeypatch):
    """Test the CLI with a custom YAML configuration file."""

    # Create a custom YAML and pass via --config
    custom = {
        "model_id": "from-file",
        "num_classes": 8,
        "data_path": "/mnt/x",
        "batch_size": 128,
        "epochs": 1,
    }
    custom_path = tmp_path / "custom.yaml"
    custom_path.write_text(yaml.dump(custom))

    captured = {}

    # pylint: disable-next=unused-argument
    def fake_tune_model(config, project_name, experiment_name):
        """Fake tune_model function to capture the config."""
        captured["cfg"] = config

    monkeypatch.setattr(
        "embedl_hub.core.tuning.tuner.tune_model", fake_tune_model
    )
    monkeypatch.setattr('embedl_hub.cli.utils.assert_api_config', lambda: None)
    monkeypatch.setattr(
        "embedl_hub.core.context.read_embedl_hub_context",
        lambda: {
            "project_name": "test_project",
            "experiment_name": "test_experiment",
        },
    )

    runner = CliRunner()
    result = runner.invoke(tune_cli, ["--config", str(custom_path)])
    assert result.exit_code == 0

    cfg = captured["cfg"]
    # should exactly reflect custom.yaml
    assert cfg.model_id == "from-file"
    assert cfg.num_classes == 8
    assert cfg.data_path == "/mnt/x"
    assert cfg.batch_size == 128
    assert cfg.epochs == 1


if __name__ == "__main__":
    pytest.main([__file__])
