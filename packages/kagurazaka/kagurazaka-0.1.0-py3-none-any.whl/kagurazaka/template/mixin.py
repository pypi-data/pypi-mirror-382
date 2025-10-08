import logging

from omegaconf import OmegaConf
logger = logging.getLogger(__name__)


KAGURAZAKA_MIXIN_PLACEHOLDER = "___KAGURAZAKA_MIXIN_PLACEHOLDER___"


def param_mixin(src, dst) -> None:
    # when src / dst is primitive, this case should update the value
    src_dict = None
    if isinstance(src, dict):
        src_dict = src
    if hasattr(src, "__dict__"):
        src_dict = src.__dict__

    dst_is_dict = isinstance(dst, dict)

    if src_dict is None or dst_is_dict is False:
        return dst

    for k, v in dst.items():
        if k in src_dict:
            src_dict[k] = param_mixin(src_dict[k], v)
        else:
            src_dict[k] = v

    return src_dict


def check_placeholder(src, parent_name=""):
    if src == KAGURAZAKA_MIXIN_PLACEHOLDER:
        logger.warning(f"Kagurazaka mixin placeholder found for field {parent_name} but no mixin is provided, some nasty thing is going to happen!")
        return True

    src_dict = None
    if isinstance(src, dict):
        src_dict = src
    if hasattr(src, "__dict__"):
        src_dict = src.__dict__

    if src_dict is None:
        return False

    ret = False
    for k, v in src_dict.items():
        ret = ret or check_placeholder(v, f"{parent_name}.{k}")
    return ret
