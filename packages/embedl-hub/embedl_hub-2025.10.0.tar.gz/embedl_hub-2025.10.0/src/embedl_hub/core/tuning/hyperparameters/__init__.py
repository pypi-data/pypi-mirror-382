# Copyright (C) 2025 Embedl AB

"""Module for tuning hyperparameters for model training."""

import pytorch_lightning as pl

from embedl_hub.core.tuning.hyperparameters.batch_size import (
    maybe_tune_batch_size,
)
from embedl_hub.core.tuning.hyperparameters.learning_rate import (
    maybe_tune_learning_rate,
)


def tune_hyperparameters(
    config,
    hub_data_module,
    hub_module,
) -> None:
    """Tune hyperparameters for model training."""

    trainer = pl.Trainer(max_epochs=-1, log_every_n_steps=1)
    hub_module.tune_hyperparameters = True
    maybe_tune_batch_size(config, trainer, hub_data_module, hub_module)
    maybe_tune_learning_rate(config, trainer, hub_data_module, hub_module)
    hub_module.tune_hyperparameters = False
