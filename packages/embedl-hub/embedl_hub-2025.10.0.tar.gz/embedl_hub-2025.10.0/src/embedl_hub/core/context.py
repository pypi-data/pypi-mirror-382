# Copyright (C) 2025 Embedl AB

"""Context manager for managing the current experiment context."""

from contextlib import contextmanager
from pathlib import Path
from typing import Dict

import typer
import yaml

from embedl_hub.core.hub_logging import console
from embedl_hub.tracking import (
    RunType,
    set_experiment,
    set_project,
    start_run,
)
from embedl_hub.tracking.utils import (
    timestamp_id,
    to_run_url,
)

CTX_FILE = Path(".embedl_hub_ctx")


def set_new_experiment(ctx: dict, experiment: str | None = None) -> None:
    """Set a new experiment in the context dict, using the given name or a generated one."""
    experiment_name = experiment or timestamp_id("experiment")
    experiment_ctx = set_experiment(experiment_name)
    ctx["experiment_id"] = experiment_ctx.id
    ctx["experiment_name"] = experiment_ctx.name


def write_ctx(ctx: Dict[str, str]) -> None:
    """Write the current embedl-hub context to the local YAML file."""
    CTX_FILE.write_text(yaml.safe_dump(ctx, sort_keys=False), encoding="utf-8")


def read_embedl_hub_context() -> Dict[str, str]:
    """Read the current embedl-hub context from the local YAML file."""
    return (
        yaml.safe_load(CTX_FILE.read_text(encoding="utf-8"))
        if CTX_FILE.exists()
        else {}
    )


def require_embedl_hub_context() -> Dict[str, str]:
    """
    Load the current embedl-hub context and ensure `project_name` and `experiment_name` are present.
    """
    ctx = read_embedl_hub_context()
    if not ctx.get("project_name") or not ctx.get("experiment_name"):
        console.print(
            "[red]Failed to find context: No project or experiment is initialized.[/]",
            "[red]Run 'embedl-hub init' to set up the context.[/]",
        )
        raise typer.Exit(1)
    return ctx


@contextmanager
def experiment_context(
    project_name: str, experiment_name: str, run_type: RunType
):
    """
    Context manager for managing the current experiment context.
    """
    try:
        project = set_project(project_name)
        experiment = set_experiment(experiment_name)

        console.log(f"Running command with project name: {project_name}")
        console.log(f"Running command with experiment name: {experiment_name}")
        with start_run(type=run_type) as run:
            run_url = to_run_url(
                project_id=project.id,
                experiment_id=experiment.id,
                run_id=run.id,
            )
            console.log(f"Track your progress at {run_url}")
            yield
            console.log(f"View results at {run_url}")
    finally:
        pass


@contextmanager
def tuning_context():
    """
    Context manager for managing the current tuning experiment context.
    """
    ctx = read_embedl_hub_context()
    project_name = ctx.get("project_name")
    experiment_name = ctx.get("experiment_name")
    run_type = RunType.TUNE
    if not experiment_name:
        experiment_name = "tuning_experiment"

    with experiment_context(project_name, experiment_name, run_type):
        yield
