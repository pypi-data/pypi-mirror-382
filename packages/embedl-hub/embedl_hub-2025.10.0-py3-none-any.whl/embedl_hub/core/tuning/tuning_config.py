# Copyright (C) 2025 Embedl AB

"""Configuration for tuning models."""

from typing import Any, Dict, List, Literal, Union

from pydantic import conlist, model_validator

from embedl_hub.core.config import ExperimentConfig


class TuningConfig(ExperimentConfig):
    """Class for tuning configuration."""

    # User specific parameters
    model_id: str
    num_classes: int
    data_path: str
    img_size: conlist(int, min_length=2, max_length=2)  # type:ignore

    # Tuning parameters
    batch_size: Union[int, Literal["auto"]]
    max_learning_rate: Union[float, Literal["auto"]]
    weight_decay: float
    epochs: int
    pre_trained: bool

    train_transforms: List[Dict[str, Any]]
    val_transforms: List[Dict[str, Any]]

    @model_validator(mode="before")
    @classmethod
    def check_required_fields(cls, value: Dict[str, Any]):
        """Check if the minimum required fields are present in the config."""

        required_fields = [
            "model_id",
            "num_classes",
            "data_path",
            "batch_size",
            "epochs",
        ]
        for field in required_fields:
            if field not in value:
                raise ValueError(f"`{field}` must be defined.")
        return value
