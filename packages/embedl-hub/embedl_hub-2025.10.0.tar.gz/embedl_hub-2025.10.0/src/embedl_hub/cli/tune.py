# Copyright (C) 2025 Embedl AB

"""CLI component for fine-tuning models."""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import CONFIG_HELPER, SIZE_HELPER

tune_cli = typer.Typer()
__all__ = ["tune_cli"]


@tune_cli.command("tune")
def tune_command(
    model_id: str = typer.Option(
        None,
        "--model_id",
        "--id",
        "-i",
        help=(
            "Model ID to fine-tune. "
            "Browse available models at https://hub.embedl.com/browse. (required)"
        ),
        show_default=False,
    ),
    num_classes: int = typer.Option(
        None,
        "--num-classes",
        "-nc",
        help="Number of output classes for the classification task. (required)",
        show_default=False,
    ),
    data_path: str = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for tuning. "
            "Supports a modified torchvision ImageFolder format. "
            "Use a single directory (e.g., /path/to/dataset) for a training-only "
            "set, or include '/train' and '/val' subdirectories for separate "
            "training and validation splits. Each subdirectory must contain one "
            "folder per class with images. (required)"
        ),
        show_default=False,
    ),
    batch_size: int = typer.Option(
        None,
        "--batch-size",
        "-b",
        help=(
            "Batch size used during training. "
            "If unset, will auto-tune to the maximum that fits in GPU memory. "
            "Auto-tuning is unavailable without a GPU, so on CPU-only systems "
            "you must set this manually."
        ),
        show_default=False,
    ),
    max_learning_rate: float = typer.Option(
        None,
        "--learning-rate",
        "-lr",
        help=(
            "Maximum learning rate of the one-cycle scheduler during optimization. "
            "Default, search for optimal learning rate."
        ),
        show_default=False,
    ),
    size: str = typer.Option(
        None,
        "--size",
        help=SIZE_HELPER,
        show_default=False,
    ),
    epochs: int = typer.Option(
        None,
        "--epochs",
        "-e",
        help="Number of training epochs. (required)",
        show_default=False,
    ),
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help=CONFIG_HELPER,
    ),
):
    """
    Fine-tune a model on your dataset.

    Required arguments (if not provided through --config):
        --model-id
        --num-classes
        --data
        --epochs

    Examples:
    ---------
    Tune the torchvision AlexNet model for 10 classes using the dataset
    at `/path/to/dataset` for 10 epochs:

        $ embedl-hub tune -i torchvision/alexnet -nc 10 -d /path/to/dataset -e 10

    Tune the torchvision ResNet50 model for 10 classes using the dataset
    at `/path/to/dataset` with custom settings from `config.yaml`:

        $ embedl-hub tune -i torchvision/resnet50 -nc 10 -d /path/to/dataset -c /path/to/config.yaml

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config, remove_none_values
    from embedl_hub.core.config import load_default_config_with_size
    from embedl_hub.core.context import require_embedl_hub_context
    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.tuning.tuner import tune_model
    from embedl_hub.core.tuning.tuning_config import TuningConfig
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    ctx = require_embedl_hub_context()

    cfg = load_default_config_with_size(TuningConfig, size, "tune")
    cli_flags = {
        "model_id": model_id,
        "num_classes": num_classes,
        "data_path": data_path,
        "batch_size": batch_size,
        "max_learning_rate": max_learning_rate,
        "epochs": epochs,
    }
    cfg = cfg.merge_yaml(other=config_path, **remove_none_values(cli_flags))
    try:
        cfg.validate_config()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

    tune_model(
        config=cfg,
        project_name=ctx["project_name"],
        experiment_name=ctx["experiment_name"],
    )
