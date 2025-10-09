# Copyright (C) 2025 Embedl AB

"""Tuning module for Embedl Hub."""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pytorch_lightning as pl
import torch
import torchmetrics
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms as T
from torchvision.datasets import ImageFolder

from embedl_hub.core.context import experiment_context
from embedl_hub.core.hub_logging import console
from embedl_hub.core.quantization.quantization_config import QuantizationConfig
from embedl_hub.core.tuning.hyperparameters import (
    tune_hyperparameters,
)
from embedl_hub.core.tuning.load_model import (
    ClassifierName,
    load_model_with_num_classes,
)
from embedl_hub.core.tuning.save_model import (
    assert_can_save_jit_model,
    save_jit_model,
)
from embedl_hub.core.tuning.tuning_config import TuningConfig
from embedl_hub.tracking import RunType, log_metric, log_param


def assert_correct_num_classes(
    config: TuningConfig,
    data_module: pl.LightningDataModule,
):
    """Assert that the number of classes in the dataset matches the config."""

    # Get the number of classes in the dataset
    num_classes = len(data_module.train_dataloader().dataset.classes)

    # Assert that the number of classes matches the config
    assert num_classes == config.num_classes, (
        f"Number of classes in dataset ({num_classes}) does not match "
        f"number of classes in config ({config.num_classes})."
    )


def _get_dataset_paths(dataset_dir: str) -> Tuple[Path, Optional[Path]]:
    """Get the dataset paths for training and validation."""

    dataset_dir_path = Path(dataset_dir)

    train_data_path = (
        dataset_dir_path / "train"
        if (dataset_dir_path / "train").exists()
        else dataset_dir_path
    )
    val_data_path = (
        dataset_dir_path / "val"
        if (dataset_dir_path / "val").exists()
        else None
    )
    return train_data_path, val_data_path


# Maps every torchvision.transforms class name to the class.
transforms_mapping = {
    key: val for key, val in T.__dict__.items() if isinstance(val, type)
}


def _decode_tranforms(transforms: List[Dict[str, Any]]):
    """Decode the transforms definitions from the config."""
    transforms_list = []
    for _transform in transforms:
        transform = deepcopy(_transform)
        transform_type = transform.pop("type")
        if transform_type not in transforms_mapping:
            raise ValueError(f"Unknown transform type: {transform_type}")
        train_transform = transforms_mapping[transform_type](**transform)
        transforms_list.append(train_transform)
    return T.Compose(transforms_list)


def prepare_data(
    config: Union[TuningConfig, QuantizationConfig],
    batch_size: Optional[int] = None,
) -> Tuple[DataLoader, Optional[DataLoader]]:
    """
    Prepare the data for training.
    """

    batch_size = batch_size or config.batch_size
    train_transforms = _decode_tranforms(config.train_transforms)

    train_data_path, val_data_path = _get_dataset_paths(config.data_path)

    # Load dataset
    train_dataset = ImageFolder(train_data_path, transform=train_transforms)
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=4,
        pin_memory=True,
    )

    if val_data_path:
        val_transforms = _decode_tranforms(config.val_transforms)
        val_dataset = ImageFolder(val_data_path, transform=val_transforms)
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
        )
        return train_dataloader, val_dataloader
    return train_dataloader, None


class HubDataModule(pl.LightningDataModule):
    """Lightning data module for tuning a model on user dataset."""

    def __init__(self, config: Union[TuningConfig, QuantizationConfig]):
        super().__init__()
        self.config = config
        # `batch_size` needs to be its own attribute to be visible for the batch size tuner.
        self.batch_size = (
            config.batch_size if isinstance(config.batch_size, int) else 1
        )

        if isinstance(config, TuningConfig):
            # Assert that the number of classes in the dataset matches the config
            # This is needed for tuning
            assert_correct_num_classes(config, self)

    def train_dataloader(self) -> DataLoader:
        return prepare_data(self.config, self.batch_size)[0]

    def val_dataloader(self) -> Optional[DataLoader]:
        return prepare_data(self.config, self.batch_size)[1]

    def calibration_dataloader(self) -> DataLoader:
        """Return a dataloader for calibration data."""
        # For quantization, we use the validation dataloader as calibration data
        val_dataloader = self.val_dataloader()
        if val_dataloader is not None:
            return val_dataloader
        # If no validation dataloader is available, use the training dataloader
        return self.train_dataloader()


class HubModule(pl.LightningModule):
    """Lightning module for tuning a model on user dataset."""

    def __init__(
        self,
        model: nn.Module,
        config: TuningConfig,
    ):
        super().__init__()
        self.model = model
        self._tracking = False
        self.track_every_n_steps = 30

        self.lr = (
            config.max_learning_rate
            if isinstance(config.max_learning_rate, float)
            else 0.0
        )
        self.weight_decay = config.weight_decay

        self.top1 = torchmetrics.Accuracy(
            "multiclass", num_classes=config.num_classes
        )
        self.val_loss = torchmetrics.MeanMetric()
        self.tune_hyperparameters = False

    @property
    def tracking(self) -> bool:
        """Whether the module is tracking metrics."""
        return self._tracking

    @tracking.setter
    def tracking(self, value: bool):
        """Set whether the module is tracking metrics."""
        self._tracking = value

    def common_step(self, batch, _batch_idx):
        """Common step for training and validation."""
        x, y = batch
        y_hat = self.model(x)
        loss = nn.functional.cross_entropy(y_hat, y)
        return loss, y_hat, y

    # pylint: disable-next=arguments-differ
    def training_step(self, batch, _batch_idx):
        """Compute the loss for a batch of data."""
        loss, _, _ = self.common_step(batch, _batch_idx)
        if self.tracking and self.global_step % self.track_every_n_steps == 0:
            log_metric("train/loss/step", loss.item(), step=self.global_step)
        return loss

    # pylint: disable-next=arguments-differ
    def validation_step(self, batch, _batch_idx):
        """
        Compute the loss and accuracy metrics for a batch of validation data.
        """
        loss, y_hat, y = self.common_step(batch, _batch_idx)
        self.val_loss.update(loss.item())
        self.top1.update(y_hat, y)
        return loss

    def on_validation_epoch_end(self):
        top1 = self.top1.compute().item()
        val_loss = self.val_loss.compute().item()
        console.log(f"Epoch {self.current_epoch}: Validation Accuracy: {top1}")
        console.log(f"Epoch {self.current_epoch}: Validation Loss: {val_loss}")
        console.log(
            f"Epoch {self.current_epoch}: Learning Rate: {self.lr_schedulers().get_last_lr()[0]}"
        )
        # Pytorch Lightning does a "sanity check" at the start of training
        # where it runs one validation step before training starts.
        # We don't want to log metrics during this step, so we check if
        # this is the first step of the first epoch.
        sanity_checking = self.global_step == 0 and self.current_epoch == 0
        if self.tracking and not sanity_checking:
            log_metric("accuracy", top1, step=self.current_epoch)
            log_metric("val/loss/step", val_loss, step=self.global_step)
        self.top1.reset()
        self.val_loss.reset()

    def find_last_layer_parameters(self) -> List[nn.Parameter]:
        """
        Find the parameters of the last layer of the model.
        This is useful for tuning only the last layer.

        Currently, we look for parameters in the model that match
        the names defined in ClassifierName, which are typically the last
        layers of the model in torchvision.

        If the model has a `get_classifier` method, we also include
        the parameters from that method, which is a method in `timm` models
        that returns the classifier layer.

        """

        params: Dict[str, nn.Parameter] = {}

        # Try get_classifier method (timm models)
        if hasattr(self.model, "get_classifier"):
            classifier = self.model.get_classifier()
            if classifier is not None:
                params.update(
                    {
                        k: v
                        for k, v in classifier.named_parameters()
                        if isinstance(v, nn.Parameter)
                    }
                )

        # Try known classifier names (torchvision models)
        for name in ClassifierName:
            if hasattr(self.model, name):
                layer = getattr(self.model, name)
                if isinstance(layer, nn.Module):
                    params.update(
                        {
                            k: v
                            for k, v in layer.named_parameters()
                            if isinstance(v, nn.Parameter)
                        }
                    )

        if not params:
            raise AssertionError(
                "Could not determine which parameters to tune."
            )
        return list(params.values())

    def configure_optimizers(self):
        param_group = ({"params": self.find_last_layer_parameters()},)
        optimizer = torch.optim.AdamW(
            param_group, lr=self.lr, weight_decay=self.weight_decay
        )
        if self.tune_hyperparameters:
            return optimizer
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=self.lr,
            epochs=self.trainer.max_epochs,
            steps_per_epoch=len(self.trainer.datamodule.train_dataloader()),
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
                "frequency": 1,
            },
        }


def log_config_params(config: TuningConfig) -> None:
    """Log the configuration parameters for tracking."""

    def _format_float(value: float) -> str:
        """Format float values for logging."""
        return (
            f"{value:.6f}".rstrip('0')
            if isinstance(value, float)
            else str(value)
        )

    def _format_img_size(value: Union[int, List[int]]) -> str:
        """Format image size for logging."""
        return str(value).strip("[]").replace(", ", "x").strip()

    log_param("model id", config.model_id)
    log_param("num classes", str(config.num_classes))
    log_param("batch size", str(config.batch_size))
    log_param("maximum learning rate", _format_float(config.max_learning_rate))
    log_param("weight decay", _format_float(config.weight_decay))
    log_param("epochs", str(config.epochs))
    log_param("image size", _format_img_size(config.img_size))
    log_param("pre-trained", str(config.pre_trained))


def tune_model(
    config: TuningConfig, project_name: str, experiment_name: str
) -> None:
    """Tune a model using the provided configuration."""

    with experiment_context(project_name, experiment_name, RunType.TUNE):
        model = load_model_with_num_classes(
            config.model_id, config.pre_trained, config.num_classes
        )
        assert_can_save_jit_model(model, config.model_id, config.img_size)

        # Find hyperparameters
        tune_hyperparameters(
            config, HubDataModule(config), HubModule(model, config)
        )

        hub_data_module = HubDataModule(config)
        hub_module = HubModule(model, config)

        # Create trainer
        trainer = pl.Trainer(max_epochs=config.epochs)

        hub_module.tracking = True
        log_config_params(config)
        # Train model
        trainer.fit(
            hub_module,
            datamodule=hub_data_module,
        )

        # Save model
        save_jit_model(model, config.model_id, config.img_size)
