# Copyright (C) 2025 Embedl AB

"""Configuration for quantizing models."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import conlist

from embedl_hub.core.config import ExperimentConfig


class QuantizationConfig(ExperimentConfig):
    """Class for tuning configuration."""

    # User specific parameters
    model: Path
    data_path: Optional[str]
    img_size: conlist(int, min_length=2, max_length=2)  # type:ignore
    output_file: Path
    num_samples: int

    batch_size: int = 1
    train_transforms: List[Dict[str, Any]]
    val_transforms: List[Dict[str, Any]]
