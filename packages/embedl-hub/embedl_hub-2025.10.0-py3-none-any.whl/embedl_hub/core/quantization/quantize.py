# Copyright (C) 2025 Embedl AB

"""Module for quantizing ONNX models using Qualcomm AI Hub."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Union

import numpy as np
import qai_hub as hub

from embedl_hub.core.context import RunType, experiment_context
from embedl_hub.core.hub_logging import console
from embedl_hub.core.onnx_utils import load_onnx_model
from embedl_hub.core.quantization.psnr import measure_psnr_between_models
from embedl_hub.core.quantization.quantization_config import QuantizationConfig
from embedl_hub.core.tuning.tuner import HubDataModule
from embedl_hub.tracking import log_param


class QuantizationError(RuntimeError):
    """Raised when Qualcomm AI Hub quantization job fails or times out."""


@dataclass
class QuantizationResult:
    """Result of a quantization job."""

    model_path: Path
    job_id: str


def _generate_random_data(
    config: QuantizationConfig, input_name: str
) -> Dict[str, List[np.ndarray]]:
    """
    Generate random calibration data for quantization.

    Args:
        config: QuantizationConfig containing img_size and num_samples.

    Returns:
        Dictionary with random calibration data.
    """
    config.num_samples = 1
    img_size = tuple(config.img_size)
    calibration_data = [np.random.rand(1, 3, *img_size).astype(np.float32)]

    return {input_name: calibration_data}


def _load_calibration_data(
    config: QuantizationConfig, input_name: str
) -> Dict[str, List[np.ndarray]]:
    """
    Load calibration data from the specified path.

    Args:
        config: QuantizationConfig containing data_path and transforms.

    Returns:
        Dictionary with calibration data.
    """
    data_module = HubDataModule(config)
    data_module.prepare_data()
    data_module.setup("validate")

    calibration_data = []
    dataloader = data_module.calibration_dataloader()
    if len(dataloader) < config.num_samples:
        config.num_samples = len(dataloader)
    for batch_idx, (img, _) in enumerate(dataloader):
        if batch_idx >= config.num_samples:
            break
        calibration_data.append(img.numpy())

    return {input_name: calibration_data}


def collect_calibration_data(
    config: QuantizationConfig,
) -> Dict[str, List[np.ndarray]]:
    """
    Collect calibration data for quantization.

    Args:
        config: QuantizationConfig containing data_path and transforms.

    Returns:
        Dictionary with calibration data.
    """
    onnx_model = load_onnx_model(config.model)
    input_names = [input.name for input in onnx_model.graph.input]
    assert len(input_names) == 1, "Model must have a single input."
    if config.data_path is None:
        return _generate_random_data(config, input_names[0])
    return _load_calibration_data(config, input_names[0])


def _save_quantized(quantized: "hub.Model", output_file: Path) -> Path:
    """
    Save the quantized artifact to a user-specified location or to the root
    directory with the name provided by Qualcomm AI Hub.

    Returns:
        Path to the saved model file.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file = Path(quantized.download(str(output_file)))
    return output_file


def log_config_params(config: QuantizationConfig) -> None:
    """Log the configuration parameters for tracking."""

    def _format_img_size(value: Union[int, List[int]]) -> str:
        """Format image size for logging."""
        return str(value).strip("[]").replace(", ", "x").strip()

    log_param("num samples", str(config.num_samples))
    log_param("image size", _format_img_size(config.img_size))


def _maybe_unzip_model(model_path: Path, tmp_folder: Path) -> Path:
    """Unzip the model if it is a zip file and return the ONNX file path."""
    if model_path.suffix == ".zip":
        with zipfile.ZipFile(model_path, 'r') as zip_ref:
            extract_path = tmp_folder / model_path.stem
            zip_ref.extractall(extract_path)
            subfolders = [f for f in extract_path.iterdir() if f.is_dir()]
            if len(subfolders) != 1:
                raise RuntimeError(
                    f"Expected exactly one folder in the zip, found: {len(subfolders)}"
                )
            only_folder = subfolders[0]
            onnx_files = list(only_folder.rglob("*.onnx"))
            if len(onnx_files) != 1:
                raise RuntimeError(
                    f"Expected exactly one .onnx file, found: {len(onnx_files)}"
                )
            return onnx_files[0]
    return model_path


def quantize_model(
    config: QuantizationConfig,
    project_name: str,
    experiment_name: str,
) -> None:
    """
    Submit an ONNX model to Qualcomm AI Hub and retrieve the compiled artifact.

    Args:
        config: QuantizationConfig containing model_path, data_path, and transforms.

    Returns:
        QuantizationResult with local path to compiled model.

    """

    with experiment_context(project_name, experiment_name, RunType.QUANTIZE):
        model_file = Path(config.model)
        if not model_file.exists():
            raise ValueError(f"Model not found: {model_file}")

        calibration_data = collect_calibration_data(config)
        log_config_params(config)

        try:
            job = hub.submit_quantize_job(
                model=model_file.as_posix(),
                weights_dtype=hub.QuantizeDtype.INT8,
                activations_dtype=hub.QuantizeDtype.INT8,
                calibration_data=calibration_data,
            )
        except Exception as error:
            raise QuantizationError(
                "Failed to submit quantization job."
            ) from error

        log_param("$qai_hub_job_id", job.job_id)

        try:
            quantized = job.get_target_model()
        except Exception as error:
            raise QuantizationError(
                "Failed to download quantized model from Qualcomm AI Hub."
            ) from error
        if quantized is None:
            raise QuantizationError(
                "Quantized model returned by Qualcomm AI Hub is None."
            )

        local_path = _save_quantized(quantized, config.output_file)
        try:
            with TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                measure_psnr_between_models(
                    model_file,
                    _maybe_unzip_model(local_path, tmpdir_path),
                    calibration_data,
                )
        except Exception as error:
            pass  # PSNR measurement is optional, ignore errors

        console.print(f"[green]✓ Quantized model saved to {local_path}[/]")
