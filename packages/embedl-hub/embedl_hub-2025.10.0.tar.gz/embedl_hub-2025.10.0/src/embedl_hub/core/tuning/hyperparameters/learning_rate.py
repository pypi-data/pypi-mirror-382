# Copyright (C) 2025 Embedl AB

"""Tune learning rate for a model."""

import pytorch_lightning as pl

from embedl_hub.core.tuning.tuning_config import TuningConfig


def tune_learning_rate(
    config: TuningConfig,
    trainer: pl.Trainer,
    hub_data_module: pl.LightningDataModule,
    hub_module: pl.LightningModule,
):
    """Automatically find learning rate for model."""
    # Tune trainer
    tuner = pl.tuner.tuning.Tuner(trainer)
    lr_finder = tuner.lr_find(
        min_lr=1e-5,
        train_dataloaders=hub_data_module.train_dataloader(),
        model=hub_module,
    )
    if lr_finder is None:
        raise ValueError("LR finder failed.")
    suggestion = lr_finder.suggestion()
    if suggestion is None:
        raise ValueError(
            "LR finder did not return a valid learning rate suggestion."
        )
    config.max_learning_rate = suggestion


def maybe_tune_learning_rate(
    config: TuningConfig,
    trainer: pl.Trainer,
    hub_data_module: pl.LightningDataModule,
    hub_module: pl.LightningModule,
) -> None:
    """Tune learning rate if set to auto."""
    if config.max_learning_rate == "auto":
        tune_learning_rate(config, trainer, hub_data_module, hub_module)
