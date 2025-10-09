# Copyright (C) 2025 Embedl AB

"""
Test for the experiment_context manager in embedl_hub.core.context
"""

import pytest

from embedl_hub.core.context import RunType, experiment_context


@pytest.fixture(autouse=True)
def mock_tracking(monkeypatch):
    """Pytest fixture to mock the tracking functions used in the experiment_context."""

    class DummyCtx:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class DummyRun:
        def __init__(self):
            self.id = "1337"
            self.name = "dummy_run"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(
        "embedl_hub.core.context.set_project",
        lambda name: DummyCtx(f"dummy_project_id_{name}", name),
    )
    monkeypatch.setattr(
        "embedl_hub.core.context.set_experiment",
        lambda name: DummyCtx(f"dummy_experiment_id_{name}", name),
    )
    monkeypatch.setattr(
        "embedl_hub.core.context.start_run",
        lambda **kwargs: DummyRun(),
    )


def test_experiment_context_logs(capsys):
    """Test that the experiment_context logs the correct messages."""

    with experiment_context(
        experiment_name="test_experiment",
        project_name="test_project",
        run_type=RunType.TUNE,
    ):
        pass

    captured = capsys.readouterr()
    messages = captured.out + captured.err

    # Check that both messages appeared
    assert "Running command with project name: test_project" in messages
    assert "Running command with experiment name: test_experiment" in messages


if __name__ == "__main__":
    pytest.main([__file__])
