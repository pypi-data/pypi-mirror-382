# Copyright (C) 2025 Embedl AB

"""Tune batch size for a model."""

from typing import Optional

import pytorch_lightning as pl
import torch

from embedl_hub.core.tuning.tuning_config import TuningConfig


def tune_batch_size(
    config: TuningConfig,
    trainer: pl.Trainer,
    hub_data_module: pl.LightningDataModule,
    hub_module: pl.LightningModule,
) -> None:
    """Find maximum batch size for a model."""

    if not torch.cuda.is_available():
        raise ValueError(
            "CUDA is not available. Batch size tuning is currently not supported on CPU."
        )

    tuner = pl.tuner.tuning.Tuner(trainer)
    auto_batch_size: Optional[int] = tuner.scale_batch_size(
        datamodule=hub_data_module,
        model=hub_module,
    )
    if auto_batch_size is None:
        raise ValueError("Auto batch size tuning failed.")
    config.batch_size = auto_batch_size


def maybe_tune_batch_size(
    config: TuningConfig,
    trainer: pl.Trainer,
    hub_data_module: pl.LightningDataModule,
    hub_module: pl.LightningModule,
) -> None:
    """Tune batch size if set to auto."""
    if config.batch_size == "auto":
        tune_batch_size(config, trainer, hub_data_module, hub_module)
