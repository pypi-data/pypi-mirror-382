import copy
import os
from typing import Any, Dict, List, Sequence, Tuple, Union

import onnx
import onnx_graphsurgeon as gs
import tensorrt as trt
import torch
from torch import nn

from ..registration import register_conversion
from ..utils.calibration import Calibrator
from ..utils.tensor_utils import flatten_arguments, get_shape_from_tensor, move_tensors


@register_conversion("onnx")
def convert_trt_with_onnx(
    model: nn.Module,
    input_args: Sequence[Tuple[Tuple[Any], Dict[str, Any]]],
    export_path: str,
    int8: bool = False,
    fp16: bool = False,
    calibrator: Union[Calibrator, None] = None,
    input_names: Union[List[str], None] = None,
    dynamic_axes: Union[
        Dict[str, Dict[int, Union[str, Tuple[str, int, int]]]], None
    ] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Converts a PyTorch model to ONNX format and then to TensorRT engine using ONNX GraphSurgeon.

    Exports the model to ONNX, sanitizes it with onnx_graphsurgeon, and builds a TensorRT engine.
    Supports INT8/FP16 precision and dynamic axes configuration.

    Args:
        model (nn.Module): The PyTorch model to convert.
        input_args (Sequence[Tuple[Tuple[Any], Dict[str, Any]]]): Input arguments for model tracing.
        export_path (str): Path to save the TensorRT engine file.
        int8 (bool, optional): Enable INT8 precision. Defaults to False.
        fp16 (bool, optional): Enable FP16 precision. Defaults to False.
        calibrator (Calibrator | None, optional): Custom calibrator for INT8. Defaults to None.
        input_names (List[str] | None, optional): Names of input tensors. Defaults to None.
        dynamic_axes (Dict[str, Dict[int, str | Tuple[str, int, int]]] | None, optional):
            Dictionary specifying dynamic axes for ONNX export. Defaults to None.
        **kwargs: Additional keyword arguments passed to torch.onnx.export.

    Returns:
        Dict[str, Any]: Conversion metadata including:
            - 'rt_mode': Always 'onnx'
            - 'input_shapes': Input tensor shapes
            - 'int8': Whether INT8 was enabled
            - 'fp16': Whether FP16 was enabled
            - 'input_names': Input tensor names if provided
            - 'dynamic_axes': Dynamic axes configuration if provided

    Raises:
        AssertionError: If input_names is missing when dynamic_axes is provided.
    """

    base_name = os.path.splitext(export_path)[0]
    onnx_path = base_name + ".onnx"
    arguments = {}
    args, keywords = input_args[0]

    arguments["args"] = (*args, keywords)

    device = torch.device("cuda")

    model.to(device)
    arguments["args"] = move_tensors(arguments["args"], device)

    arguments.update({"model": model, "f": onnx_path})

    if input_names is not None:
        arguments["input_names"] = input_names
    if dynamic_axes is not None:
        assert input_names is not None, (
            "input_names must be specified if dynamic_axes need to set"
        )
        onnx_dynamic_axes: Dict[str, Dict[int, str]] = {}
        for name, axes in dynamic_axes.items():
            onnx_dynamic_axes[name] = {}
            for axis, axes in axes.items():
                if isinstance(axes, tuple):
                    onnx_dynamic_axes[name][axis] = axes[0]
                else:
                    onnx_dynamic_axes[name][axis] = axes

        arguments["dynamic_axes"] = onnx_dynamic_axes

    torch.onnx.export(**arguments)

    # sanitize onnx with onnx_graphsurgeon
    graph = gs.import_onnx(onnx.load(onnx_path))
    graph.fold_constants().cleanup()

    onnx.save(gs.export_onnx(graph), onnx_path)
    model.cpu()

    # convert onnx to trt with TensorRT backend
    builder = trt.Builder(trt.Logger(trt.Logger.INFO))
    config = builder.create_builder_config()

    if int8:
        config.set_flag(trt.BuilderFlag.INT8)
        if calibrator is not None:
            config.int8_calibrator = calibrator
        else:
            config.int8_calibrator = Calibrator(
                input_args,
                algorithm=trt.CalibrationAlgoType.MINMAX_CALIBRATION,
                cache_file=base_name + ".cache",
            )
    if fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    config.profiling_verbosity = trt.ProfilingVerbosity.DETAILED
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )

    # build optimization profile
    if dynamic_axes is not None:
        profile = builder.create_optimization_profile()
        args = list(input_args)

        if all([isinstance(arg, torch.Tensor) for arg in args]):
            flatten_args: List[torch.Tensor] = args
        else:
            flatten_args = flatten_arguments(input_args)
        for name, axes in dynamic_axes.items():
            if input_names is not None and name in input_names:
                idx = input_names.index(name)

            default_shape = list(flatten_args[idx].shape)
            min_shape = copy.deepcopy(default_shape)
            max_shape = copy.deepcopy(default_shape)
            for axis, value in axes.items():
                if isinstance(value, tuple):
                    _, min_el, max_el = value
                    min_shape[axis] = min_el
                    max_shape[axis] = max_el

            profile.set_shape(name, min_shape, default_shape, max_shape)
            config.add_optimization_profile(profile)

    parser = trt.OnnxParser(network, trt.Logger())

    parser.parse_from_file(onnx_path)

    engine = builder.build_serialized_network(network, config)

    print("build engine")
    with open(export_path, "wb") as f:
        f.write(engine)

    del engine, builder, config, network, parser

    ret = {
        "rt_mode": "onnx",
        "input_shapes": get_shape_from_tensor(arguments["args"][:-1]),
        "int8": int8,
        "fp16": fp16,
    }
    if input_names is not None:
        ret["input_names"] = input_names
    if dynamic_axes is not None:
        ret["dynamic_axes"] = dynamic_axes

    return ret
