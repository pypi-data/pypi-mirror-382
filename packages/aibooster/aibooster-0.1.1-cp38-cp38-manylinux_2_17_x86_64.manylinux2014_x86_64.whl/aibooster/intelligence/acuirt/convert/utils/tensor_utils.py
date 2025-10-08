from collections.abc import Mapping, Sequence
from typing import Union

import torch

type_cannot_recursived = (str,)


def move_tensors(data: Union[Sequence, Mapping, torch.Tensor], device):
    # move dict, list nested tensors to cuda
    if isinstance(data, type_cannot_recursived):
        return data
    elif isinstance(data, Mapping):
        return {key: move_tensors(value, device) for key, value in data.items()}
    elif isinstance(data, Sequence):
        return type(data)([move_tensors(item, device) for item in data])
    elif isinstance(data, torch.Tensor):
        return data.to(device)
    else:
        return data


def get_shape_from_tensor(data):
    if isinstance(data, type_cannot_recursived):
        return data
    elif isinstance(data, Mapping):
        return {key: get_shape_from_tensor(value) for key, value in data.items()}
    elif isinstance(data, Sequence):
        return type(data)([get_shape_from_tensor(item) for item in data])
    elif torch.is_tensor(data):
        return tuple(data.shape)
    else:
        return data


def make_tensor(input, device):
    if isinstance(input, (list, tuple)) and all(type(x) is int for x in input):
        return torch.randn(input, device=device)
    if isinstance(input, dict):
        return {key: make_tensor(value, device) for key, value in input.items()}
    if isinstance(input, (list, tuple)):
        return type(input)([make_tensor(x, device) for x in input])
    return input


def flatten_arguments(input):
    result = []
    if isinstance(input, Mapping):
        for el in input.values():
            result.extend(flatten_arguments(el))
    elif isinstance(input, Sequence):
        for el in input:
            result.extend(flatten_arguments(el))
    else:
        result.append(input)
    return result
