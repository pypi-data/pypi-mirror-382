# Copyright (C) 2025 Embedl AB
"""
Project and experiment context management for embedl-hub CLI.

This module provides CLI commands to initialize and display the current project
and experiment context. The selected context determines under which project and
experiment all data, results, and metadata are stored in the user's account on
https://hub.embedl.com.

Users can create new projects and experiments, switch between them, and view the
active context. Context information is stored locally in a YAML file.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.table import Table

init_cli = typer.Typer(help="Initialise / show project & experiment context")


@init_cli.command("init")
def init_command(
    project: Optional[str] = typer.Option(
        None, "-p", "--project", help="Project name or id", show_default=False
    ),
    experiment: Optional[str] = typer.Option(
        None,
        "-e",
        "--experiment",
        help="Experiment name or id",
        show_default=False,
    ),
):
    """
    Create new or load existing project and/or experiment.

    Examples
    --------
    Create new project and experiment (random names):

        $ embedl-hub init

    Create new or load existing project called `My Flower Detector App`:

        $ embedl-hub init -p "My Flower Detector App"

    Create new or load existing experiment `MobileNet Flower Detector` inside the
    current project (omit name for random ID):

        $ embedl-hub init -e "MobileNet Flower Detector"

    Create new or load existing project and experiment with names `My Flower Detector App`
    and `MobileNet Flower Detector` (omit names for random names):

        $ embedl-hub init -p "My Flower Detector App" -e "MobileNet Flower Detector"

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import (
        read_embedl_hub_context,
        set_new_experiment,
        write_ctx,
    )
    from embedl_hub.core.hub_logging import console
    from embedl_hub.tracking import set_project
    from embedl_hub.tracking.utils import (
        timestamp_id,
        to_experiment_url,
    )
    # pylint: enable=import-outside-toplevel

    assert_api_config()

    ctx = (
        {}
        if project is None and experiment is None
        else read_embedl_hub_context()
    )

    if experiment and not (project or ctx):
        console.print(
            "[red]✗[/] No project initialized; run with --project first"
        )
        raise typer.Exit(1)

    # Set or switch project if needed
    if project is not None or not ctx:
        project_name = project or timestamp_id("project")
        project_ctx = set_project(project_name)
        ctx = {  # Reset context on new project
            "project_id": project_ctx.id,
            "project_name": project_ctx.name,
        }
        # Always set a new experiment when a new project is created or switched to
        set_new_experiment(ctx, experiment)
    elif "project_id" in ctx and "project_name" in ctx:
        set_project(ctx["project_name"])
        # Set experiment if given, or if missing in context
        if experiment or "experiment_id" not in ctx:
            set_new_experiment(ctx, experiment)
    else:
        console.print(
            "[red]✗[/] No project initialized, run `embedl-hub init -p <name>` first."
        )
        raise typer.Exit(1)

    write_ctx(ctx)

    console.print(f"[green]✓ Project:[/] {ctx['project_name']}")
    console.print(f"[green]✓ Experiment:[/] {ctx['experiment_name']}")
    console.print(
        f"See your results: {to_experiment_url(ctx['project_id'], ctx['experiment_id'])}"
    )

    if project is not None and experiment is None:
        console.print(
            "[yellow]Note:[/] A new experiment created because no experiment name was specified. "
            "To continue an existing experiment, use -e <experiment>."
        )


@init_cli.command("show")
def show_command():
    """Print active project/experiment IDs and names."""

    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.context import read_embedl_hub_context
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    ctx = read_embedl_hub_context()

    if not ctx:
        console.print("[red]✗[/] No project or experiment initialized.")
        console.print(
            "Run `embedl-hub init` to create a new project and experiment."
        )
        return

    table = Table(title=".embedl_hub_ctx", show_lines=True, show_header=False)
    for k in (
        "project_id",
        "project_name",
        "experiment_id",
        "experiment_name",
    ):
        table.add_row(k, ctx.get(k, "—"))
    console.print(table)
