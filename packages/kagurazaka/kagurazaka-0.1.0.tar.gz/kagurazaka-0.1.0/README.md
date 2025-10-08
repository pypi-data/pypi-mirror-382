# Kagurazaka

- [Kagurazaka](#kagurazaka)
  - [Installation](#installation)
  - [Usage](#usage)
    - [`mp` Backbone](#mp-backbone)
    - [`torch_vanilla_single` Backbone](#torch_vanilla_single-backbone)
  - [Basic Task Definition](#basic-task-definition)
    - [Normal Task (i.e. CPU Task) - `KagurazakaTask`](#normal-task-ie-cpu-task---kagurazakatask)
    - [Torch Task Vanilla V1 - `KagurazakaVanillaTorchTaskV1`](#torch-task-vanilla-v1---kagurazakavanillatorchtaskv1)
  - [Task Template Decorators](#task-template-decorators)
    - [Normal Task Template `@moemoecue_normal`](#normal-task-template-moemoecue_normal)
    - [Torch Task Vanilla V1 Template `@moemoecue_torch_vanilla_v1`](#torch-task-vanilla-v1-template-moemoecue_torch_vanilla_v1)
  - [Configuration - Mixin, YAML, CLI and Template](#configuration---mixin-yaml-cli-and-template)
  - [Reserved Keywords](#reserved-keywords)
  - [Reserved CLI Arguments](#reserved-cli-arguments)
  - [Roadmap](#roadmap)

Dynamic task dispatching and data processing framework.

To be brief, kagurazaka abstract any workload into the following two parts:

- Executor (Backbone): Execution model (e.g. process / thread pool, GPU, etc.)
- Task: The real workload to be executed

Given a task, kagurazaka will enable you to easily dispatch the workload, featuring:

- Argument parsing through CLI, YAML, or both, with the flexibility to override the default values and mixin the code if defined
- Sharding support, including hard sharding (data sharded) and soft sharding (index sharded)
- Cache management, avoiding redundant computation
- Automatic parallelization by specifying the backbone through single command line option

Kagurazaka also helps the task definition to be concise and reusable by providing a template compilation system.

Please refer to [Basic Task Definition](#basic-task-definition) and [Task Template Decorators](#task-template-decorators) for more details.

## Installation

```bash
pip install kagurazaka
```

For development,

```bash
pip install -e .
```

## Usage

General usage of kagurazaka is as follows:

```bash
$ kagurazaka -hk
usage: kagurazaka [--backbone {auto,mp,torch_vanilla_single}] [--mixin-cfg MIXIN_CFG] [--mixin MIXIN [MIXIN ...]] [-h] [-hb] [-hk] task_file_path task_name

Dynamically load a Python class from a module.

positional arguments:
  task_file_path        The file path of the task file
  task_name             The name of the task class to use

options:
  --backbone {auto,mp,torch_vanilla_single}
                        The backbone to use (default: auto)
  --mixin-cfg MIXIN_CFG
                        The file path of the mixin config file to use.
  --mixin MIXIN [MIXIN ...]
                        The mixin to use. Has higher priority than --mixin-cfg. Provide in the format of "key=value".
  -h, --help            Show help message for task and exit
  -hb, --help-backbone  Show help message for chosen backbone and exit
  -hk, --help-kagurazaka
                        Show Kagurazaka help message and exit
```

Different backbones might support different additional arguments.

### `mp` Backbone

Using process pool as execution model to parallelize the task.

```bash
$ kagurazaka ... ... -hb
usage: kagurazaka [--num_process NUM_PROCESS] [--chunksize CHUNKSIZE] [-hb]

Kagurazaka MP Backbone.

options:
  --num_process NUM_PROCESS
                        Number of processes to use, for normal task (default: number of CPU cores)
  --chunksize CHUNKSIZE
                        Number of tasks to be sent to a worker process at a time, for normal task (default: 1)
  -hb, --help-backbone  Show help message for chosen backbone and exit
```

### `torch_vanilla_single` Backbone

Using a single GPU and PyTorch dataloader as execution model to parallelize the task.

```bash
$ kagurazaka ... ... -hb
usage: kagurazaka [--device DEVICE] [-hb]

Kagurazaka Torch Vanilla Single GPU Backbone.

options:
  --device DEVICE       The device to use
  -hb, --help-backbone  Show help message for chosen backbone and exit
```

## Basic Task Definition

### Normal Task (i.e. CPU Task) - [`KagurazakaTask`](./kagurazaka/task/normal.py)

Following methods should be implemented in the subclass:

- `def __init__(self, args) -> None`
  - Initialize the task with command line arguments
  - `args` can be passed to `ArgumentParser.parse_args()` to parse remaining command line arguments
- `def generate_tasks(self) -> list`
  - Return a list of workload inputs, each element is a dictionary of the workload input
- `def is_executed(self, **kwargs) -> bool`
  - Check if the task has already been executed
  - `**kwargs` is the input of the task (contents released by `generate_tasks`)
- `def process(self, **kwargs) -> None`
  - Process the task
  - `**kwargs` is the input of the task (contents released by `generate_tasks`)

### Torch Task Vanilla V1 - [`KagurazakaVanillaTorchTaskV1`](./kagurazaka/task/torch_vanilla.py)

Following methods should be implemented in the subclass (for each section, choose one of the options):

**Model / Dataloader**

- `def load_model(self, device) -> None`: Load the model on a device
- `def get_dataset(self) -> Dataset`: Return a Dataset object, **each element should always be a dict**
- `def get_dataloader(self) -> DataLoader`: Return a DataLoader object

**Bookkeeping**

Option A - Easiest:

- `def is_each_executed(self, **kwargs) -> bool`
  - Check if the task has already been executed for each element in the batch
  - `**kwargs` is the input of the task (contents released from the result of dict in `dataset`)

Option B - If the above's expressiveness is not enough, i.e. check needs to done on the batch level, here is the second option:

- `def is_executed(self, batch) -> bool`
  - Check if the task has already been executed
  - `batch` is the input of the task (the batch got from the `dataloader`)

**Process**

Option A - Easiest:

- `def inference(self, device, batch_size, **batch) -> torch.Tensor | dict | list`
  - Inference the batch
  - `**batch` is the input of the task (the batch got from the `dataloader`)
  - return value can be a tensor, a dict, or a list
- `def postprocess_each(self, batch_idx, batch_size, **input_batch_and_result) -> None`
  - Postprocess each element in the batch
  - `**input_batch_and_result` consists of two parts
    - `**batch`: the input of the task (the batch got from the `dataloader`)
    - `result` (if `result` is a tensor or a list) or `**result` (if `result` is a dict): the result of the inference

Option B - If `postprocess_each` is not enough

* Replace `postprocess_each` in option A with `postprocess`
  * `def postprocess(self, batch_size, results, **batch) -> None`

Option C - If the whole stuff is not enough, i.e. you want to take over the whole process, here is the third option

* `def process(self, device, batch) -> None`
  * Only implement this method
  * `device` is the device to use
  * `batch` is the input of the task (the batch got from the `dataloader`)

## Task Template Decorators

Template decorators can help to simplify the task definition by providing a set of default methods and fields.

### Normal Task Template [`@moemoecue_normal`](./kagurazaka/template/task/normal.py)

Following compulsory methods can be omitted upon using the template decorator.

- `def generate_tasks(self) -> list`
  - When `input_mode` is not `None`
- `def is_executed(self, **kwargs) -> bool`
  - When `finish_check_mode` is not `None` and `output_mode` is not `None`

Further, following parameter injection will be done automatically

- `input` to `**kwargs` in `process(...)` and `is_executed(...)`
  - When `input_mode` is not `None`
- `output` to `**kwargs` in `process(...)` and `is_executed(...)`
  - When `output_mode` is not `None`
- Other fields might also be injected to `**kwargs` based on the `input_mode` and `output_mode`

### Torch Task Vanilla V1 Template [`@moemoecue_torch_vanilla_v1`](./kagurazaka/template/task/torch_vanilla.py)

Following compulsory methods can be omitted upon using the template decorator.

- `def get_dataset(self) -> Dataset`
  - When `input_mode` is not `None` and `def load_data(self, **kwargs) -> dict` is implemented
- `def get_dataloader(self) -> DataLoader`
  - When `dataloader` (dataloader parameters, except `dataset`) is not `None`
- `def is_each_executed(self, **kwargs) -> bool`
  - When `finish_check_mode` is not `None` and `output_mode` is not `None`

Further, following parameter injection will be done automatically

- `input` to `batch`, and to whereever `batch` is released
- `output` to `postprocess_each`
- Other fields might also be injected to `batch` based on the `input_mode`
- Other fields might also be injected to `postprocess_each` based on the `output_mode`

> [!IMPORTANT]
> As mentioned, for `input_mode` to take effect for this template, the torch task should also implement [`KagurazakaVanillaTorchMixinV1`](./kagurazaka/template/task/torch_vanilla.py).

## Configuration - Mixin, YAML, CLI and Template

In this section, we will briefly introduce the template configuration options for kagurazaka.

Notice that when using template decorators, some fields are compulsory but might differ from trial to trial. Thus here we provide a placeholder and mixin mechanism to make the task definition more flexible.

For any field (even inside a dict or class), one can define it as a placeholder by setting it to `KAGURAZAKA_MIXIN_PLACEHOLDER`. When the task is loaded, the placeholder will be replaced with the true value of the field through the mixin mechanism.

The mixin process is as follows:

- Highest priority: CLI arguments `--mixin`, which is a list of "key=value" pairs
- Second highest priority: YAML file specified by `--mixin-cfg`
- Least priority: original value of the field

Example: for the following template decorator:

```python
@moemoecue_normal(
  hard_shard_mode=NoHardShard(
    input_path=KAGURAZAKA_MIXIN_PLACEHOLDER,
    output_path=KAGURAZAKA_MIXIN_PLACEHOLDER
  ),
  soft_shard=SoftShard(
    shard_idx=0,
    shard_num=1,
  ),
  input_mode=InputByExts(exts=[".py"]),
  output_mode=OutputByFilenameSubfoldering(file_to_write=KAGURAZAKA_MIXIN_PLACEHOLDER),
  finish_check_mode=FinishCheckByOutputFileExistence(output_field_suffix=KAGURAZAKA_MIXIN_PLACEHOLDER)
)
class TestTask(KagurazakaTask):
  pass
```

we can provide a YAML file like this:

```yaml
output_mode:
  file_to_write:
    test: "test.txt"
finish_check_mode:
  output_field_suffix: "test"
```

and specify the input / output through CLI arguments:

```bash
$ kagurazaka <TASK_FILE_PATH> <TASK_CLASS_NAME> --mixin-cfg <YAML_PATH> --mixin hard_shard_mode.input_path=<INPUT_PATH> --mixin hard_shard_mode.output_path=<OUTPUT_PATH> 
```

## Reserved Keywords

When defining the task and designing the field names, please avoid using the following keywords:

- Used in torch task processing
  - `result`
- Used by template decorators
  - `input`
  - `output`
  - `output_*`

## Reserved CLI Arguments

- `-h`, `--help`
  - Show help message for task and exit
- `-hb`, `--help-backbone`
  - Show help message for chosen backbone and exit
- `-hk`, `--help-kagurazaka`
  - Show Kagurazaka help message and exit
- `--backbone`
  - The backbone to use (default: auto)
- `--mixin-cfg`
  - The file path of the mixin config file to use.
- `--mixin`
  - The mixin to use. Has higher priority than `--mixin-cfg`. Provide in the format of "key=value".

## Roadmap

- [ ] Sharding tool
- [ ] File triplet jsonl exporter
- [ ] CPU affinity
