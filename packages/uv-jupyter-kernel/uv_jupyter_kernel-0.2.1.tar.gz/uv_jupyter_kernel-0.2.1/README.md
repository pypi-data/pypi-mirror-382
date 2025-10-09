# uv-jupyter-kernel

Script to configure Jupyter kernels that use the [uv](https://github.com/astral-sh/uv) environment and dependency manager. It allows you to create isolated kernels for different Python versions, making it easier to use Jupyter with controlled and reproducible environments.

## Requirements
- Some Jupyter client (e.g., VSCode extension)
- [uv](https://github.com/astral-sh/uv) installed and available in the PATH

## Usage

```bash
uvx uv-jupyter-kernel --versions 3.13 3.12
```

By default, the script configures kernels for Python versions 3.13 and 3.12. You can specify other versions by passing them as arguments.

This will create (or update) kernel files at `~/.local/share/jupyter/kernels/uv-<version>/kernel.json`, allowing you to select the corresponding kernel for the desired Python version within Jupyter.

## What does the script do?
- Locates the `uv` executable on the system.
- For each specified Python version, creates a Jupyter kernel that:
  - Ephemerally installs `ipykernel` and starts the executor itself.
  - Ensures the `uv` PATH is available in the kernel environment.
  - Allows each notebook to run in an independent, ephemeral, and isolated environment.

## Advantages
- The only thing that needs to be available initially is uv.
- Ephemeral environments: each notebook has its own and can install new dependencies with `uv pip install`; when Jupyter is restarted, the environment is reset.
- No need to install Jupyter in the environment: less chance of dependency conflicts.
- Shared cache: each thing can be downloaded only once and then reused.

## Disadvantages
- Higher disk usage if your system does not support hardlinks (e.g., Termux on Android)

