try:
    import torch  # noqa
except ImportError:
    print(
        "Error: AcuiRT requires PyTorch but it is not installed. Please install PyTorch."
    )
    raise

try:
    import torchvision  # noqa
except ImportError:
    print(
        "Error: AcuiRT requires torchvision but it is not installed. Please install torchvision."
    )
    raise

from . import convert, inference, profile

__all__ = ["convert", "inference", "profile"]
