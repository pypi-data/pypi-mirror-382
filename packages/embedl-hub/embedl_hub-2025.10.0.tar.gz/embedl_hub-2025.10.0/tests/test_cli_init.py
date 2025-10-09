# Copyright (C) 2025 Embedl AB
"""
Test cases for the embedl-hub CLI init command.

"""

import pytest
import yaml
from typer.testing import CliRunner

from embedl_hub.cli.init import init_cli
from embedl_hub.core.context import CTX_FILE


class DummyCtx:
    def __init__(self, id, name):
        self.id = id
        self.name = name


@pytest.fixture(autouse=True)
def mock_tracking(monkeypatch):
    monkeypatch.setattr(
        "embedl_hub.tracking.set_project",
        lambda name: DummyCtx(f"dummy_project_id_{name}", name),
    )
    monkeypatch.setattr(
        "embedl_hub.core.context.set_experiment",
        lambda name: DummyCtx(f"dummy_experiment_id_{name}", name),
    )
    monkeypatch.setattr("embedl_hub.cli.utils.assert_api_config", lambda: None)


runner = CliRunner()


@pytest.fixture(autouse=True)
def cleanup_ctx_file():
    """
    Pytest fixture to ensure the context file (.embedl_hub_ctx) is removed
    before and after each test. This prevents tests from interfering with each
    other by guaranteeing a clean state.
    """
    if CTX_FILE.exists():
        CTX_FILE.unlink()
    yield
    if CTX_FILE.exists():
        CTX_FILE.unlink()


def test_init_new_project():
    """Test creating a new project with the -p flag."""
    result = runner.invoke(init_cli, ["init", "-p", "MyProject"])
    assert result.exit_code == 0
    assert "✓ Project:" in result.output
    assert "✓ Experiment:" in result.output
    ctx = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx["project_name"] == "MyProject"
    assert ctx["project_id"] == "dummy_project_id_MyProject"
    assert (
        ctx["experiment_name"].startswith("experiment_")
        or ctx["experiment_name"]
    )
    assert ctx["experiment_id"].startswith("dummy_experiment_id_")


def test_init_new_experiment():
    """Test creating a new experiment with the -e flag in an existing project."""
    runner.invoke(init_cli, ["init", "-p", "MyProject"])
    result = runner.invoke(init_cli, ["init", "-e", "MyExperiment"])
    assert result.exit_code == 0
    assert "✓ Experiment:" in result.output
    ctx = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx["experiment_name"] == "MyExperiment"
    assert ctx["experiment_id"] == "dummy_experiment_id_MyExperiment"


def test_init_no_project_error():
    """Test error when creating an experiment without an initialized project."""
    result = runner.invoke(init_cli, ["init", "-e", "MyExperiment"])
    assert result.exit_code != 0
    assert "No project initialized" in result.output


def test_init_default_project_and_experiment():
    """Test creating a default project and experiment with no flags."""
    result = runner.invoke(init_cli, ["init"])
    assert result.exit_code == 0
    assert "✓ Project:" in result.output
    assert "✓ Experiment:" in result.output
    ctx = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx["project_id"].startswith("dummy_project_id_project_")
    assert ctx["experiment_id"].startswith("dummy_experiment_id_experiment_")
    assert ctx["project_name"].startswith("project_")
    assert ctx["experiment_name"].startswith("experiment_")


def test_switch_project_resets_experiment():
    """Switching project should reset experiment context."""
    runner.invoke(init_cli, ["init", "-p", "Proj1", "-e", "Exp1"])
    ctx1 = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    runner.invoke(init_cli, ["init", "-p", "Proj2"])
    ctx2 = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx2["project_name"] == "Proj2"
    assert ctx2["project_id"] == "dummy_project_id_Proj2"
    assert ctx2["project_id"] != ctx1["project_id"]
    assert ctx2["experiment_id"] != ctx1["experiment_id"]


def test_show_command_outputs_context():
    """Test the show command prints the current context."""
    runner.invoke(init_cli, ["init", "-p", "ShowProj", "-e", "ShowExp"])
    result = runner.invoke(init_cli, ["show"])
    assert result.exit_code == 0
    assert ".embedl_hub_ctx" in result.output
    assert "project_id" in result.output
    assert "experiment_id" in result.output
    assert "ShowProj" in result.output
    assert "ShowExp" in result.output


def test_ctx_file_created_and_updated():
    """Test that the context file is created and updated as expected."""
    assert not CTX_FILE.exists()
    runner.invoke(init_cli, ["init", "-p", "FileTestProj"])
    assert CTX_FILE.exists()
    ctx = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx["project_name"] == "FileTestProj"
    assert ctx["project_id"] == "dummy_project_id_FileTestProj"
    runner.invoke(init_cli, ["init", "-e", "FileTestExp"])
    ctx2 = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    assert ctx2["experiment_name"] == "FileTestExp"
    assert ctx2["experiment_id"] == "dummy_experiment_id_FileTestExp"


def test_init_always_creates_new_project_and_experiment(monkeypatch):
    """Test that running 'init' with no flags always creates a new project and experiment."""
    import itertools

    project_counter = itertools.count()
    experiment_counter = itertools.count()

    monkeypatch.setattr(
        "embedl_hub.tracking.set_project",
        lambda name: DummyCtx(
            f"dummy_project_id_{next(project_counter)}", name
        ),
    )
    monkeypatch.setattr(
        "embedl_hub.core.context.set_experiment",
        lambda name: DummyCtx(
            f"dummy_experiment_id_{next(experiment_counter)}", name
        ),
    )
    # First run: create initial context
    result1 = runner.invoke(init_cli, ["init"])
    assert result1.exit_code == 0
    ctx1 = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    project_id_1 = ctx1["project_id"]
    experiment_id_1 = ctx1["experiment_id"]
    # Second run: should create a new project and experiment, not reuse the old ones
    result2 = runner.invoke(init_cli, ["init"])
    assert result2.exit_code == 0
    ctx2 = yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
    project_id_2 = ctx2["project_id"]
    experiment_id_2 = ctx2["experiment_id"]
    assert project_id_2 != project_id_1, (
        "Project ID should change on each init with no flags"
    )
    assert experiment_id_2 != experiment_id_1, (
        "Experiment ID should change on each init with no flags"
    )


if __name__ == "__main__":
    pytest.main([__file__])
