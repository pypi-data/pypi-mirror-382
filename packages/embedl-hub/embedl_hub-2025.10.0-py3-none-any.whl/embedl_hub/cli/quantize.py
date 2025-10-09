# Copyright (C) 2025 Embedl AB

"""
embedl-hub quantize - send an onnx model to Qualcomm AI Hub and retrieve a
quantized onnx model.
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    CONFIG_HELPER,
    OUTPUT_FILE_HELPER,
    SIZE_HELPER,
)

quantize_cli = typer.Typer()


@quantize_cli.command("quantize")
def quantize_command(
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to the ONNX model file, or to a directory containing the ONNX model "
        "and any associated data files, to be quantized. (required)",
        show_default=False,
    ),
    data_path: str = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for calibration. "
            "Supports a modified torchvision ImageFolder format. Use a single "
            "directory (e.g., /path/to/dataset) for a training-only set, or "
            "provide a structure with '/train' and '/val' subdirectories (e.g."
            ", /path/to/dataset/train and /path/to/dataset/val) to enable "
            "separate training and validation splits. Each subdirectory should "
            "contain one folder per class with corresponding images. If both "
            "train and val directories are provided, calibration will use the "
            "validation set. If no data path is provided, random data will be "
            "generated for calibration."
        ),
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    num_samples: int = typer.Option(
        None,
        "--num-samples",
        "-n",
        help="Number of data samples to use during quantization calibration.",
        show_default=False,
    ),
    size: str = typer.Option(
        None,
        "--size",
        help=SIZE_HELPER,
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
    Quantize an ONNX model using Qualcomm AI Hub.
    Qualcomm AI Hub may return a zip file containing multiple files.

    Required arguments (if not provided through --config):
        --model

    Examples
    --------
    Quantize the ONNX model `exported_model.onnx` calibrating on data
    from `/path/to/dataset/` using 1000 samples from the dataset:

        $ embedl-hub quantize -m exported_model.onnx -d /path/to/dataset/ -n 1000

    Quantize the ONNX model using the configuration specified in `my_config.yaml`:

        $ embedl-hub quantize -c ./my_config.yaml

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config, remove_none_values
    from embedl_hub.core.config import load_default_config_with_size
    from embedl_hub.core.context import require_embedl_hub_context
    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.quantization.quantization_config import (
        QuantizationConfig,
    )
    from embedl_hub.core.quantization.quantize import (
        quantize_model,
    )
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    ctx = require_embedl_hub_context()

    if not output_file:
        output_file = Path(model).with_suffix(".quantized")
        console.print(
            f"[yellow]No output file specified, using default: {output_file}[/]"
        )

    cfg = load_default_config_with_size(QuantizationConfig, size, "quantize")

    # Data path needs special handling:
    # 1. If the path is None (default), we want to keep it None
    #    so that random data is generated.
    # 2. If the path is provided via CLI or config file, we want to
    #    override the default None value.
    # Therefore, we first merge with None, then with the actual value.
    cfg = cfg.merge_yaml(other=None, **{"data_path": data_path})
    cli_flags = remove_none_values(
        {
            "model": model,
            "output_file": output_file,
            "num_samples": num_samples,
            "data_path": data_path,
        }
    )
    cfg = cfg.merge_yaml(other=config_path, **cli_flags)
    try:
        cfg.validate_config()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

    quantize_model(
        config=cfg,
        project_name=ctx["project_name"],
        experiment_name=ctx["experiment_name"],
    )
