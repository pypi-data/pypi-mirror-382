from typing import Any, Callable, Dict, Sequence, Tuple, Union

from torch import nn

CONVERSION_REGISTRY: Dict[
    str,
    Callable[
        [
            nn.Module,
            Union[
                Sequence[Tuple[Tuple[Any], Dict[str, Any]]],
                Tuple[Tuple[Any], Dict[str, Any]],
            ],
            str,
        ],
        dict,
    ],
] = {}


def register_conversion(name: str):
    def decorator(func):
        CONVERSION_REGISTRY[name] = func
        return func

    return decorator
