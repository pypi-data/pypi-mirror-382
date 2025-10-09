# Copyright (C) 2025 Embedl AB

"""Save a model after tuning."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import torch
from torch import nn

from embedl_hub.core.hub_logging import console
from embedl_hub.core.tuning.load_model import clean_model_id


def _save_jit_to_path(
    model: nn.Module,
    model_id: str,
    image_size: List[int],
    save_path: Path,
) -> Path:
    example_data = torch.randn(1, 3, *image_size)
    clean_model_name = clean_model_id(model_id)

    saved_model_path = save_path / f"{clean_model_name}_tuned.pt"

    torch.jit.save(
        torch.jit.script(model, example_inputs=[(example_data,)]),
        saved_model_path,
    )
    return saved_model_path


def save_jit_model(
    model: nn.Module, model_id: str, image_size: List[int]
) -> None:
    """Save a model in current working directory using TorchScript."""
    saved_model_path = _save_jit_to_path(
        model,
        model_id,
        image_size,
        Path.cwd(),
    )
    console.print(
        f"[green]✓ Model {model_id} saved as TorchScript model at {saved_model_path}[/]"
    )


def assert_can_save_jit_model(
    model: nn.Module, model_id: str, image_size: List[int]
) -> None:
    """Assert that the model can be saved as a TorchScript model."""
    with TemporaryDirectory() as temp_dir:
        try:
            _save_jit_to_path(model, model_id, image_size, Path(temp_dir))
        except Exception as e:
            raise RuntimeError(
                f"Model {model_id} cannot be saved as a TorchScript model. "
                f"Error: {e}"
            ) from e
