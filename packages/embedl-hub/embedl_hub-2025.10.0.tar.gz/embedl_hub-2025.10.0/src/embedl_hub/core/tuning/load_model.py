# Copyright (C) 2025 Embedl AB

"""Load a model from the Embedl Hub."""

from enum import StrEnum

from timm import create_model, list_pretrained
from torch import nn
from torchvision.models import get_model, get_model_weights


def _change_num_classes_linear(linear_layer, num_classes: int):
    """Change the number of classes in a linear layer."""
    return nn.Linear(
        in_features=linear_layer.in_features,
        out_features=num_classes,
        bias=linear_layer.bias is not None,
    )


def change_num_classes_linear(
    layer_name: str, model: nn.Module, num_classes: int
):
    """Change the number of classes in a linear layer."""
    linear_layer = getattr(model, layer_name)
    new_linear_layer = _change_num_classes_linear(linear_layer, num_classes)
    setattr(model, layer_name, new_linear_layer)


def change_num_classes_sequential(
    layer_name: str, model: nn.Module, num_classes: int
):
    """Change the number of classes in a sequential layer."""

    def _recursive_search_for_linear(layer: nn.Module, num_classes: int):
        if isinstance(layer, nn.Linear):
            sequential_layer[-1] = _change_num_classes_linear(
                layer, num_classes
            )
        elif isinstance(layer, nn.Sequential):
            _recursive_search_for_linear(sequential_layer[-1], num_classes)

    sequential_layer = getattr(model, layer_name)
    _recursive_search_for_linear(sequential_layer, num_classes)


class ClassifierName(StrEnum):
    """Enum for classifier names in torchvision models."""

    CLASSIFIER = "classifier"
    FC = "fc"
    HEAD = "head"
    HEADS = "heads"


# Map model names to their classifier layer type
model_to_classifier_type = {
    "alexnet": ClassifierName.CLASSIFIER,
    "convnext_base": ClassifierName.CLASSIFIER,
    "convnext_large": ClassifierName.CLASSIFIER,
    "convnext_small": ClassifierName.CLASSIFIER,
    "convnext_tiny": ClassifierName.CLASSIFIER,
    "densenet101": ClassifierName.CLASSIFIER,
    "densenet121": ClassifierName.CLASSIFIER,
    "densenet161": ClassifierName.CLASSIFIER,
    "densenet169": ClassifierName.CLASSIFIER,
    "densenet201": ClassifierName.CLASSIFIER,
    "efficientnet_b0": ClassifierName.CLASSIFIER,
    "efficientnet_b1": ClassifierName.CLASSIFIER,
    "efficientnet_b2": ClassifierName.CLASSIFIER,
    "efficientnet_b3": ClassifierName.CLASSIFIER,
    "efficientnet_b4": ClassifierName.CLASSIFIER,
    "efficientnet_b5": ClassifierName.CLASSIFIER,
    "efficientnet_b6": ClassifierName.CLASSIFIER,
    "efficientnet_b7": ClassifierName.CLASSIFIER,
    "efficientnet_v2_l": ClassifierName.CLASSIFIER,
    "efficientnet_v2_m": ClassifierName.CLASSIFIER,
    "efficientnet_v2_s": ClassifierName.CLASSIFIER,
    "googlenet": ClassifierName.FC,
    "inception_v3": ClassifierName.FC,
    "maxvit_t": ClassifierName.CLASSIFIER,
    "mnasnet0_5": ClassifierName.CLASSIFIER,
    "mnasnet0_75": ClassifierName.CLASSIFIER,
    "mnasnet1_0": ClassifierName.CLASSIFIER,
    "mnasnet1_3": ClassifierName.CLASSIFIER,
    "mobilenet_v2": ClassifierName.CLASSIFIER,
    "mobilenet_v3_large": ClassifierName.CLASSIFIER,
    "mobilenet_v3_small": ClassifierName.CLASSIFIER,
    "regnet_x_16gf": ClassifierName.FC,
    "regnet_x_1_6gf": ClassifierName.FC,
    "regnet_x_32gf": ClassifierName.FC,
    "regnet_x_3_2gf": ClassifierName.FC,
    "regnet_x_400mf": ClassifierName.FC,
    "regnet_x_800mf": ClassifierName.FC,
    "regnet_x_8gf": ClassifierName.FC,
    "regnet_y_128gf": ClassifierName.FC,
    "regnet_y_16gf": ClassifierName.FC,
    "regnet_y_1_6gf": ClassifierName.FC,
    "regnet_y_32gf": ClassifierName.FC,
    "regnet_y_3_2gf": ClassifierName.FC,
    "regnet_y_400mf": ClassifierName.FC,
    "regnet_y_800mf": ClassifierName.FC,
    "regnet_y_8gf": ClassifierName.FC,
    "resnet101": ClassifierName.FC,
    "resnet152": ClassifierName.FC,
    "resnet18": ClassifierName.FC,
    "resnet34": ClassifierName.FC,
    "resnet50": ClassifierName.FC,
    "resnext101_32x8d": ClassifierName.FC,
    "resnext101_64x4d": ClassifierName.FC,
    "resnext50_32x4d": ClassifierName.FC,
    "shufflenet_v2_x0_5": ClassifierName.FC,
    "shufflenet_v2_x1_0": ClassifierName.FC,
    "shufflenet_v2_x1_5": ClassifierName.FC,
    "shufflenet_v2_x2_0": ClassifierName.FC,
    "swin_b": ClassifierName.HEAD,
    "swin_s": ClassifierName.HEAD,
    "swin_t": ClassifierName.HEAD,
    "swin_v2_b": ClassifierName.HEAD,
    "swin_v2_s": ClassifierName.HEAD,
    "swin_v2_t": ClassifierName.HEAD,
    "vgg11": ClassifierName.CLASSIFIER,
    "vgg11_bn": ClassifierName.CLASSIFIER,
    "vgg13": ClassifierName.CLASSIFIER,
    "vgg13_bn": ClassifierName.CLASSIFIER,
    "vgg16": ClassifierName.CLASSIFIER,
    "vgg16_bn": ClassifierName.CLASSIFIER,
    "vgg19": ClassifierName.CLASSIFIER,
    "vgg19_bn": ClassifierName.CLASSIFIER,
    "vit_b_16": ClassifierName.HEADS,
    "vit_b_32": ClassifierName.HEADS,
    "vit_h_14": ClassifierName.HEADS,
    "vit_l_16": ClassifierName.HEADS,
    "vit_l_32": ClassifierName.HEADS,
    "wide_resnet101_2": ClassifierName.FC,
    "wide_resnet50_2": ClassifierName.FC,
}


def _load_torchvision_model(clean_name: str, pre_trained: bool) -> nn.Module:
    """Create a torchvision model."""
    weights_enum = get_model_weights(clean_name)
    if pre_trained:
        weights = weights_enum.DEFAULT
    else:
        weights = None
    model = get_model(clean_name, weights=weights)
    model.eval()
    return model


def clean_model_id(model_id: str) -> str:
    """
    Clean the model_id to get the model name.

    1. Remove the source prefix (e.g., "torchvision-")
    2. Remove the quantization suffix (e.g., "-int8")
    """

    source_prefixes = ("torchvision-", "timm-")
    quantization_suffixes = ("-int8", "-fp16", "-fp32", "-mixed")

    if not any(model_id.startswith(prefix) for prefix in source_prefixes):
        raise ValueError("Model ID must contain a valid source prefix.")
    if not any(model_id.endswith(suffix) for suffix in quantization_suffixes):
        raise ValueError("Model ID must contain a valid quantization suffix.")

    model_id_components = model_id.split("-")[
        1:-1
    ]  # Remove source prefix and suffix
    return "_".join(model_id_components).lower()


def load_model_from_torchvision(model_id: str, pre_trained: bool) -> nn.Module:
    """Load a model from torchvision.

    Args:
        model_id (str): The ID of the model to load.
        pre_trained (bool): Whether to load the pre-trained weights.
    """

    clean_name = clean_model_id(model_id)
    return _load_torchvision_model(clean_name, pre_trained)


def change_num_classes(
    model_id: str, model: nn.Module, num_classes: int
) -> nn.Module:
    """Change the number of classes in the model.

    Args:
        model_id (str): The ID of the model.
        model (nn.Module): The model to modify.
        num_classes (int): The new number of classes.
    """
    try:
        clean_name = clean_model_id(model_id)
        classifier_type = model_to_classifier_type[clean_name].value
    except KeyError as e:
        raise ValueError(
            f"Model {model_id} is currently not supported for fine tuning. "
        ) from e
    last_layer = getattr(model, classifier_type)
    if isinstance(last_layer, nn.Linear):
        class_changer = change_num_classes_linear
    elif isinstance(last_layer, nn.Sequential):
        class_changer = change_num_classes_sequential
    else:
        raise ValueError(
            f"Unsupported classifier type {type(last_layer)} for model {model_id}."
        )
    class_changer(classifier_type, model, num_classes)
    return model


def load_torchvision_with_num_classes(
    model_id: str, pre_trained: bool, num_classes: int
) -> nn.Module:
    """Load a torchvision model with a specific number of classes."""
    model = load_model_from_torchvision(model_id, pre_trained)
    return change_num_classes(model_id, model, num_classes)


def model_id_to_timm_name(model_id: str) -> str:
    """Find a timm model with a specific ID."""
    clean_name = clean_model_id(model_id)
    for timm_name in list_pretrained():
        if timm_name.replace(".", "_").casefold() == clean_name.casefold():
            return timm_name
    raise ValueError(f"Model {model_id} not found in timm models.")


def load_timm_with_num_classes(
    model_id: str, pre_trained: bool, num_classes: int
) -> nn.Module:
    """Load a timm model with a specific number of classes."""

    model_name = model_id_to_timm_name(model_id)
    model = create_model(
        model_name, pretrained=pre_trained, num_classes=num_classes
    )
    return model


def load_model_with_num_classes(
    model_id: str, pre_trained: bool, num_classes: int
) -> nn.Module:
    """Load a model with a specific number of classes."""
    if model_id.startswith("torchvision-"):
        return load_torchvision_with_num_classes(
            model_id, pre_trained, num_classes
        )
    if model_id.startswith("timm-"):
        return load_timm_with_num_classes(model_id, pre_trained, num_classes)
    raise ValueError(
        f"Model {model_id} is currently not supported for fine tuning. "
        "Only torchvision and timm models are supported."
    )
