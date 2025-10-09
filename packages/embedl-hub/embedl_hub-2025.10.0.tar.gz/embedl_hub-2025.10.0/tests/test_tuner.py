# Copyright (C) 2025 Embedl AB

"""Tests for the tuning module and related functions."""

import pytest
import torch
from torch import nn
from torchvision.transforms import (
    Compose,
    Normalize,
    RandomCrop,
    Resize,
    ToTensor,
)

from embedl_hub.core.tuning.load_model import (
    load_model_from_torchvision,
    load_model_with_num_classes,
    load_timm_with_num_classes,
)
from embedl_hub.core.tuning.tuner import (
    HubModule,
    _decode_tranforms,
    transforms_mapping,
)


@pytest.mark.parametrize(
    ["model_id", "correct_case"],
    [
        ["torchvision-alexnet-int8", True],
        ["TORCHVISION-ALEXNET-INT8", False],
        ["TorchVision-AlexNet-Int8", False],
    ],
)
def test_load_alexnet_from_hub(model_id: str, correct_case: bool):
    """
    Test loading alexnet from the hub with different casing.

    This checks that the model ID is case-sensitive and that the model can be loaded correctly.
    """
    if not correct_case:
        with pytest.raises(ValueError):
            load_model_from_torchvision(model_id, pre_trained=False)
        return
    model = load_model_from_torchvision(model_id, pre_trained=False)
    assert model is not None


def test_load_unknown_model_from_hub():
    """Test loading an unknown model from the hub."""
    with pytest.raises(ValueError):
        load_model_from_torchvision(
            "torchvision/unknown_model", pre_trained=False
        )


def test_transforms_mapping_contains_known_class():
    """Sanity check that our mapping picked up torchvision classes."""
    assert "Resize" in transforms_mapping
    assert transforms_mapping["Resize"] is Resize


def test_decode_empty_list_returns_empty_compose():
    """Test that the composition can be empty."""
    comp = _decode_tranforms([])
    assert isinstance(comp, Compose)
    # Compose stores its list in .transforms
    assert comp.transforms == []


def test_decode_single_transform_by_name():
    """Test that a single transform can be decoded."""
    cfg = [{"type": "ToTensor"}]
    comp = _decode_tranforms(cfg)
    assert isinstance(comp, Compose)
    assert len(comp.transforms) == 1
    assert isinstance(comp.transforms[0], ToTensor)


def test_decode_with_parameters():
    """Test that parameterized transforms can be decoded."""
    cfg = [
        {"type": "RandomCrop", "size": (10, 20), "padding": 4},
        {"type": "Resize", "size": 50},
        {"type": "Normalize", "mean": [0.5, 0.5, 0.5], "std": [0.1, 0.1, 0.1]},
    ]
    comp = _decode_tranforms(cfg)
    transforms = comp.transforms

    assert isinstance(transforms[0], RandomCrop)
    assert transforms[0].size == (10, 20)
    assert transforms[0].padding == 4

    assert isinstance(transforms[1], Resize)
    # Resize stores target size under .size
    assert transforms[1].size == 50

    assert isinstance(transforms[2], Normalize)
    assert pytest.approx(transforms[2].mean) == [0.5, 0.5, 0.5]
    assert pytest.approx(transforms[2].std) == [0.1, 0.1, 0.1]


def test_decode_multiple_ordering_preserved():
    """Test that the ordering of transforms is preserved."""
    cfg = [
        {"type": "Resize", "size": 32},
        {"type": "ToTensor"},
        {"type": "Normalize", "mean": [0.0], "std": [1.0]},
    ]
    comp = _decode_tranforms(cfg)
    types = [type(t) for t in comp.transforms]
    assert types == [Resize, ToTensor, Normalize]


def test_unknown_transform_type_raises():
    """Check that unknown transforms raises value error."""
    cfg = [{"type": "NotARealTransform", "foo": "bar"}]
    with pytest.raises(ValueError) as excinfo:
        _decode_tranforms(cfg)
    assert "Unknown transform type: NotARealTransform" in str(excinfo.value)


def test_load_timm_model_from_hub():
    """Test loading a timm model from the hub."""
    with pytest.raises(ValueError):
        load_timm_with_num_classes(
            "timm-unknown_model", pre_trained=False, num_classes=1000
        )

    # Assuming we have a valid timm model ID
    model = load_timm_with_num_classes(
        "timm-tinynet_e_in1k-int8", pre_trained=False, num_classes=1000
    )
    assert model is not None
    assert hasattr(model, "forward")


def test_load_torchvision_model_with_num_classes():
    """Test loading a torchvision model with a specific number of classes."""
    model = load_model_with_num_classes(
        "torchvision-resnet18-int8", pre_trained=False, num_classes=10
    )
    assert model is not None
    assert hasattr(model, "forward")
    # Check if the last layer has the correct number of classes
    assert model.fc.out_features == 10


def test_load_timm_model_with_num_classes():
    """Test loading a timm model with a specific number of classes."""
    model = load_model_with_num_classes(
        "timm-tinynet_e_in1k-int8", pre_trained=False, num_classes=10
    )
    assert model is not None
    assert hasattr(model, "forward")
    # Check if the last layer has the correct number of classes
    assert model.classifier.out_features == 10


class DummyConfig:
    def __init__(
        self, num_classes=2, max_learning_rate=0.01, weight_decay=0.0
    ):
        self.num_classes = num_classes
        self.max_learning_rate = max_learning_rate
        self.weight_decay = weight_decay


def test_find_last_layer_parameters_with_classifier_name():
    """Test finding last layer parameters by classifier name."""

    # Create a model with a layer name matching ClassifierName
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(10, 2)

        def forward(self, x):
            return self.fc(x)

    model = DummyModel()
    config = DummyConfig()
    hub_module = HubModule(model, config)
    params = hub_module.find_last_layer_parameters()
    # Should find the 'fc' layer parameters
    assert any(isinstance(p, nn.Parameter) for p in params)
    # All returned params should require grad
    assert all(p.requires_grad for p in params)
    # Should include the fc layer's weight and bias
    fc_params = list(model.fc.parameters())
    for p in fc_params:
        assert any(torch.equal(p.data, q.data) for q in params), (
            f"Parameter {p} not found in params"
        )


def test_find_last_layer_parameters_with_get_classifier():
    """Test finding last layer parameters using get_classifier method."""

    # Model with get_classifier method (like timm)
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.classifier = nn.Linear(10, 2)

        def forward(self, x):
            return self.classifier(x)

        def get_classifier(self):
            return self.classifier

    model = DummyModel()
    config = DummyConfig()
    hub_module = HubModule(model, config)
    params = hub_module.find_last_layer_parameters()
    classifier_params = list(model.classifier.parameters())
    for p in classifier_params:
        assert any(torch.equal(p.data, q.data) for q in params), (
            f"Parameter {p} not found in params"
        )


def test_find_last_layer_parameters_with_both_methods():
    """Test finding last layer parameters with both classifier name and get_classifier."""

    # Model with both a matching name and get_classifier
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(10, 2)

        def forward(self, x):
            return self.fc(x)

        def get_classifier(self):
            return self.fc

    model = DummyModel()
    config = DummyConfig()
    hub_module = HubModule(model, config)
    params = hub_module.find_last_layer_parameters()
    # Should not duplicate parameters
    fc_params = list(model.fc.parameters())
    # All fc params should be present, but not duplicated (compare by identity)
    assert all(sum(q is p for q in params) == 1 for p in fc_params)


def test_find_last_layer_parameters_raises_if_none_found():
    """Test that an error is raised if no parameters are found."""

    # Model with no matching classifier names and no get_classifier
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Conv2d(3, 3, 1)

        def forward(self, x):
            return self.conv(x)

    model = DummyModel()
    config = DummyConfig()
    hub_module = HubModule(model, config)
    with pytest.raises(
        AssertionError, match="Could not determine which parameters to tune."
    ):
        hub_module.find_last_layer_parameters()


if __name__ == "__main__":
    pytest.main([__file__])
