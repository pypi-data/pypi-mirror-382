import os
from collections.abc import Callable
from typing import Any, Dict, Iterable, Tuple, Union

import torch
from torch import nn

from ..convert.converter import auto_preprocess
from ..convert.registration import CONVERSION_REGISTRY
from ..convert.utils.tensor_utils import make_tensor


def convert_model_kernel(
    model: nn.Module,
    config: dict,
    export_path: str,
    skip_exist: bool,
    argument_infos: Any,
    logger: Any,
) -> dict:
    """Convert model based on configuration settings.

    Args:
        model (nn.Module): PyTorch model to convert
        config (dict): Conversion configuration dictionary
        export_path (str): Base path for exporting converted model
        skip_exist (bool): Whether to skip existing conversion files
        argument_infos (Any): Input argument information for conversion
        logger (Any): Logger object for tracking conversion progress

    Returns:
        dict: Conversion summary with updated configuration
    """
    if "rt_mode" in config:
        # get basic settings from config
        export_path += ".trt"
        if skip_exist and os.path.exists(export_path):
            print(f"{export_path} exists, skip")
            return config
        else:
            print(f"convert {export_path}")

            if config.get("auto", False):
                rt_mode = "auto"
                config["conversion_mode"] = config.pop("rt_mode")
            else:
                rt_mode = config.pop("rt_mode")
            input_args = config.pop("input_args", None)
            input_shapes = config.pop("input_shapes", None)

            assert input_args is None or input_shapes is None, (
                "input_args and input_shapes cannot be both specified"
            )

            if len(list(model.parameters())) == 0:
                device = torch.device("cuda")
            else:
                device = next(model.parameters()).device

            if input_shapes is not None:
                input_args = make_tensor(input_shapes, device)
                assert isinstance(input_args, tuple)
            inputs = [(input_args, {})]

            conversion_fn = CONVERSION_REGISTRY[rt_mode]
            summary = conversion_fn(
                model,
                inputs,
                export_path,
                argument_infos=argument_infos,
                logger=logger,
                **config,
            )
            print(f"converted {export_path}")

            return summary
    else:
        ret_cfg: dict = {}
        for key, value in config.items():
            summary = convert_model_kernel(
                getattr(model, key),
                value,
                export_path + f"_{key}",
                skip_exist,
                argument_infos=argument_infos,
                logger=logger,
            )
            ret_cfg[key] = summary
        return ret_cfg


def convert_model(
    model: nn.Module,
    config: dict,
    export_path: str,
    skip_exist: bool,
    data_loader: Union[Iterable[Union[Tuple[Tuple, Dict], Dict]], None] = None,
    data_loader_post_process: Union[Callable, None] = None,
    logger=None,
):
    """Convert model with preprocessing and postprocessing.

    Args:
        model (nn.Module): PyTorch model to convert
        config (dict): Conversion configuration dictionary
        export_path (str): Base path for exporting converted model
        skip_exist (bool): Whether to skip existing conversion files
        data_loader (Union[Iterable[Dict], None], optional): Data loader for preprocessing. Defaults to None.
        data_loader_post_process (Union[Callable, None], optional): Postprocessing function for data loader. Defaults to None.
        logger (optional): Logger object for tracking conversion progress. Defaults to None.

    Returns:
        dict: Conversion configuration dictionary
    """

    if not os.path.exists(export_path):
        os.makedirs(export_path)
    export_path = os.path.join(export_path, "model")

    ret = auto_preprocess(model, data_loader, data_loader_post_process)
    ret_cfg = convert_model_kernel(model, config, export_path, skip_exist, ret, logger)

    def trim_none_dict(input: dict):
        for key in list(input.keys()):
            if input[key] is None:
                input.pop(key)
            elif isinstance(input[key], dict):
                input[key] = trim_none_dict(input[key])
            if key in input and input[key] == {}:
                input.pop(key)
        return input

    return trim_none_dict(ret_cfg)
