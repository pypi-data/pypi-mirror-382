# Copyright (C) 2025 Embedl AB

"""
embedl-hub compile - send an ONNX model to Qualcomm AI Hub, retrieve a
device-specific binary (.tflite for tflite, .bin for qnn, or .onnx for onnxruntime).
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import DEVICE_HELPER, OUTPUT_FILE_HELPER

compile_cli = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=True,
)


@compile_cli.command("compile")
def compile_command(
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to the ONNX model file, or to a directory containing the ONNX model "
        "and any associated data files, to be compiled.",
        show_default=False,
    ),
    device: str = typer.Option(
        ...,
        "-d",
        "--device",
        help=DEVICE_HELPER,
        show_default=False,
    ),
    runtime: str = typer.Option(
        "tflite",
        "-r",
        "--runtime",
        help="Runtime backend for compilation: tflite, qnn, or onnx.",
    ),
    quantize_io: bool = typer.Option(
        False,
        "--quantize-io",
        help="Quantize input and output tensors. "
        "Improves performance on platforms that support quantized I/O.",
        show_default=True,
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
    Compile an ONNX model into a device ready binary using Qualcomm AI Hub.
    Qualcomm AI Hub may return a zip file containing multiple files.

    Required arguments:
        --model
        --device

    Examples
    --------
    Compile the ONNX model `int8_model.onnx` for the Samsung Galaxy S24 and runtime (tflite):

        $ embedl-hub compile -m int8_model.onnx -d "Samsung Galaxy S24"

    Compile the ONNX model `fp32_model.onnx` for the Samsung Galaxy S24 using the tflite runtime:

        $ embedl-hub compile -m fp32_model.onnx -d "Samsung Galaxy S24" -r tflite

    Compile the ONNX model `model.onnx` for the Samsung Galaxy S24
    and save the output to `./my_outputs/model.tflite`:

        $ embedl-hub compile -m model.onnx -d "Samsung Galaxy S24" -o ./my_outputs/model.tflite

    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.compile import CompileError, CompileResult, compile_model
    from embedl_hub.core.context import require_embedl_hub_context
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    ctx = require_embedl_hub_context()

    if not output_file:
        output_file = model.with_suffix(f".{runtime}").as_posix()
        console.print(
            f"[yellow]No output file specified, using {output_file}[/]"
        )

    try:
        res: CompileResult = compile_model(
            project_name=ctx["project_name"],
            experiment_name=ctx["experiment_name"],
            model_file=model,
            device=device,
            runtime=runtime,
            quantize_io=quantize_io,
            output_file=output_file,
        )
        console.print(f"[green]✓ Compiled model for {res.device}[/]")

        # TODO: upload artifacts / metrics to web
    except (CompileError, ValueError) as error:
        console.print(f"[red]✗ {error}[/]")
        raise typer.Exit(1)
