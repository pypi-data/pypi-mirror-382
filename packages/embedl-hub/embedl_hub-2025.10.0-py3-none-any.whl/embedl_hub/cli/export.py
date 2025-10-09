# Copyright (C) 2025 Embedl AB

"""
embedl-hub export - send torch script model to Qualcomm AI Hub and retrieve an onnx model.
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    DEVICE_HELPER,
    OUTPUT_FILE_HELPER,
    SIZE_HELPER,
)

export_cli = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=True,
)


@export_cli.command("export")
def export_command(
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to the TorchScript model file to be exported.",
        show_default=False,
    ),
    size: str = typer.Option(
        ...,
        "--size",
        "-s",
        help=SIZE_HELPER,
        show_default=False,
    ),
    device: str = typer.Option(
        ...,
        "-d",
        "--device",
        help=DEVICE_HELPER
        + " Exporting for a specific device can improve compatibility.",
        show_default=False,
    ),
    output_file: str = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
):
    """
    Compile a TorchScript model into an ONNX model using Qualcomm AI Hub.
    Qualcomm AI Hub may return a zip file containing multiple files.

    Required arguments:
        --model
        --size
        --device

    Examples
    --------
    Export the TorchScript model `tuned_model.pt` with input size 224x224
    for the Samsung Galaxy S24:

        $ embedl-hub export -m tuned_model.pt --size 224,224 --device "Samsung Galaxy S24"

    Export the TorchScript model `tuned_model.pt` with input size 224x224
    for the Samsung Galaxy S24, and save it to `./my_outputs/model.onnx`:

        $ embedl-hub export -m tuned_model.pt  --size 224,224 --device "Samsung Galaxy S24" -o ./my_outputs/model.onnx

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import prepare_image_size
    from embedl_hub.core.compile import CompileError, export_model
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    if not model:
        raise ValueError("Please specify a model to export using --model")
    if not size:
        raise ValueError(
            "Please specify input image size using --size, e.g. 224,224"
        )
    if not output_file:
        output_file = model.with_suffix(".onnx").as_posix()
        console.print(
            f"[yellow]No output file specified, using {output_file}[/]"
        )
    image_size = prepare_image_size(size)
    try:
        export_model(
            model_file=model,
            device=device,
            output_file=output_file,
            image_size=image_size,
        )
        console.print("[green]✓ Exported model to ONNX[/]")

        # TODO: upload artifacts / metrics to web
    except (CompileError, ValueError) as error:
        console.print(f"[red]✗ {error}[/]")
        raise typer.Exit(1)
