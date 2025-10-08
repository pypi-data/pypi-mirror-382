import os


from .task.normal import KagurazakaTask
from .task.torch_vanilla import KagurazakaVanillaTorchTaskV1

from .template.task.normal import template_normal as moemoecue_normal
from .template.task.torch_vanilla import template_torch_vanilla_v1 as moemoecue_torch_vanilla_v1

from .template.task.torch_vanilla import KagurazakaVanillaTorchMixinV1
