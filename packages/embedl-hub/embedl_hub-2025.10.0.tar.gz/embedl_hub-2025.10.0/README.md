# Embedl Hub Python library

[Embedl Hub](https://hub.embedl.com) is a platform for building efficient edge AI applications.
With Embedl Hub, you can:

- Find the best model for your application using on-device benchmarks.
- Fine-tune the model on your own dataset and benchmark it on your target device.
- Deploy your application with the confidence that your model meets your performance requirements.

The Embedl Hub Python library (`embedl-hub`) lets you interact with Embedl Hub in scripts
and from your terminal. [Create a free Embedl Hub account](https://hub.embedl.com/docs#getting-started)
to get started with the `embedl-hub` library.

## Installation

The simplest way to install `embedl-hub` is through `pip`:

```shell
pip install embedl-hub
```

## Quickstart

We recommend using our end-to-end workflow CLI to quickly get started building your edge AI application:

```shell
 Usage: embedl-hub [OPTIONS] COMMAND [ARGS]...

 embedl-hub end-to-end Edge-AI workflow CLI


╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -V               Print embedl-hub version and exit.                                   │
│ --verbose             -v      INTEGER  Increase verbosity (-v, -vv, -vvv).                                  │
│ --install-completion                   Install completion for the current shell.                            │
│ --show-completion                      Show completion for the current shell, to copy it or customize the   │
│                                        installation.                                                        │
│ --help                                 Show this message and exit.                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ init           Create new or load existing project and/or experiment.                                       │
│ show           Print active project/experiment IDs and names.                                               │
│ tune           Fine-tune a model on your dataset.                                                           │
│ export         Compile a TorchScript model into an ONNX model using Qualcomm AI Hub.                        │
│ quantize       Quantize an ONNX model using Qualcomm AI Hub.                                                │
│ compile        Compile an ONNX model into a device ready binary using Qualcomm AI Hub.                      │
│ benchmark      Benchmark compiled model on device and measure it's performance.                             │
│ list-devices   List all available target devices.                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## License

Copyright (C) 2025 Embedl AB

This software is subject to the [Embedl Hub Software License Agreement](https://hub.embedl.com/embedl-hub-sla.txt).

<!-- Copyright (C) 2025 Embedl AB -->
