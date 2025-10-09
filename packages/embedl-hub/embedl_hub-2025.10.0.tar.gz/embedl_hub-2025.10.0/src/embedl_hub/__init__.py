# Copyright (C) 2025 Embedl AB

"""
Public Embedl Hub library API.
```pycon
>>> import embedl_hub
>>> embedl_hub.__version__
'2025.9.0'
```
"""

import importlib.metadata

from embedl_hub.core.context import tuning_context
from embedl_hub.tracking import log_metric, log_param

__all__ = ['tuning_context', 'log_metric', 'log_param']

try:
    __version__ = importlib.metadata.version("embedl_hub")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
