import sys

import torch

from ..inference.inference import TRTInferenceEngine


def profile_recursive_module(func, enable_trace=False, *args, **kwargs):
    """Profile recursive module execution with CUDA NVTX tracing.

    This function enables detailed performance profiling by wrapping the target function
    with NVTX range markers. When enable_trace is True, it pushes a new NVTX range for each
    function call and pops it on return, providing hierarchical profiling information.

    Args:
        func (Callable): Function to profile
        enable_trace (bool): Whether to enable NVTX tracing
        *args: Variable length positional arguments for the target function
        **kwargs: Arbitrary keyword arguments for the target function

    Returns:
        Any: The result of the target function execution

    Note:
        Requires torch.cuda.nvtx for tracing. Uses sys.settrace to monitor function calls.
    """

    def trace_calls(frame, event, arg):
        if event == "call":
            f_name = frame.f_code.co_name
            if "self" in frame.f_locals:
                module = frame.f_locals["self"]
                cls_name = module.__class__.__name__
                if (
                    isinstance(module, TRTInferenceEngine)
                    and module.class_name is not None
                ):
                    cls_name = module.class_name
                torch.cuda.nvtx.range_push(f"{cls_name}.{f_name}")
            else:
                torch.cuda.nvtx.range_push(f"{f_name}")
        elif event == "return":
            torch.cuda.nvtx.range_pop()
        return trace_calls

    if enable_trace:
        sys.settrace(trace_calls)
        res = func(*args, **kwargs)
        sys.settrace(None)
    else:
        res = func(*args, **kwargs)
    return res
