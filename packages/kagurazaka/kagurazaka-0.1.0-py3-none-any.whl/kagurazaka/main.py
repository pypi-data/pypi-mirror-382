import argparse
import os
import importlib.util
from omegaconf import OmegaConf
import inspect


from . import KagurazakaTask
from . import KagurazakaVanillaTorchTaskV1


def load_task_from_file(file_path, task_name):
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Load module spec
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, task_name)


def main():
    parser = argparse.ArgumentParser(description='Dynamically load a Python class from a module.', add_help=False)
    parser.add_argument('task_file_path', type=str, help='The file path of the task file')
    parser.add_argument('task_name', type=str, help='The name of the task class to use')
    parser.add_argument('--backbone', type=str, help='The backbone to use (default: auto)', default='auto', choices=['auto', 'mp', 'torch_vanilla_single'])
    parser.add_argument('--mixin-cfg', type=str, help='The file path of the mixin config file to use.', default=None)
    parser.add_argument('--mixin', type=str, nargs='+', help='The mixin to use. Has higher priority than --mixin-cfg. Provide in the format of "key=value".', default=[])

    parser.add_argument('-h', '--help', action='store_true', help='Show help message for task and exit')
    parser.add_argument('-hb', '--help-backbone', action='store_true', help='Show help message for chosen backbone and exit')
    parser.add_argument('-hk', '--help-kagurazaka', action='help', help='Show Kagurazaka help message and exit')
    args, remaining_args = parser.parse_known_args()

    if args.mixin_cfg is not None:
        mixin_args = OmegaConf.load(args.mixin_cfg)
    else:
        mixin_args = OmegaConf.create({})
    if args.mixin is not None:
        mixin_args = OmegaConf.merge(mixin_args, OmegaConf.from_dotlist(args.mixin))
    mixin_args = OmegaConf.to_container(mixin_args)

    if args.help:
        remaining_args += ["-h"]
    if args.help_backbone:
        remaining_args += ["-hb"]

    loaded_task = load_task_from_file(args.task_file_path, args.task_name)
    print(f"Successfully loaded task '{args.task_name}' from module '{args.task_file_path}'.")

    if inspect.isfunction(loaded_task):
        loaded_class = loaded_task(mixin_args)
    elif inspect.isclass(loaded_task):
        loaded_class = loaded_task
    else:
        raise ValueError("The loaded task is not a function or a class.")

    backbone = args.backbone

    if issubclass(loaded_class, KagurazakaTask):
        if backbone == 'auto': backbone = 'mp'
    if issubclass(loaded_class, KagurazakaVanillaTorchTaskV1):
        if backbone == 'auto': backbone = 'torch_vanilla_single'

    if backbone == 'mp':
        from .backbone.mp import process
    elif backbone == 'torch_vanilla_single':
        from .backbone.torch_vanilla_single import process
    else:
        raise ValueError(f"The backbone {backbone} is not supported.")

    process(loaded_class, remaining_args)
