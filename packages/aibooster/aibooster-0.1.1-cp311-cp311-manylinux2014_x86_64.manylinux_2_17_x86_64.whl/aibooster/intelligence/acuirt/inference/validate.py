import torch
from torch import nn

from ..convert.utils.tensor_utils import move_tensors
from .inference import load_runtime_module


def validate_trt_modules(
    model: nn.Module,
    rt_mode: str,
    engine_path: str,
    argument_infos: dict,
):
    rt_model = load_runtime_module(model, rt_mode, engine_path)
    arguments = argument_infos["arguments"][id(model)]

    def validate_batch(
        model: nn.Module,
        rt_model,
        argument,
    ):
        args, kwargs = argument
        model.cuda()
        if len(list(model.parameters())) == 0:
            device = torch.device("cuda")
        else:
            device = next(model.parameters()).device
        args = move_tensors(args, device)

        try:
            with torch.no_grad():
                returns = model.forward(*args).detach().cpu()
            ret = rt_model.forward(*args).detach().cpu()
        except Exception as e:
            print(e)
            print("Failed to validate trt modules")
            return None
        finally:
            model.cpu()
        if not isinstance(ret, (tuple, list)):
            ret = (ret,)

        def calc_snr(orig_out: torch.Tensor, trt_out: torch.Tensor):
            p_sig = orig_out.square().mean()
            err = orig_out - trt_out

            p_err = err.square().mean()
            if p_err == 0:
                return torch.inf
            else:
                return 10.0 * torch.log10(p_sig / p_err).item()

        error = [calc_snr(a, b) for a, b in zip(ret, returns)]
        return error

    error = []
    for idx in range(1):
        args = arguments[idx]
        ret = validate_batch(model, rt_model, args)
        if ret is None:
            return None
        error.append(ret)
    del rt_model
    return torch.tensor(error)
