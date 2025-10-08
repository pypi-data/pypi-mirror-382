import os
import glob
import json
from dataclasses import dataclass
from typing import Any, List, Optional

from ..utils.io import walk_files_of_dir


@dataclass
class FileTriplet:
    path: str
    rel_dir: str
    file_name: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "rel_dir": self.rel_dir,
            "file_name": self.file_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileTriplet":
        return cls(
            path=data["path"],
            rel_dir=data["rel_dir"],
            file_name=data["file_name"]
        )

try:
    # monkey patch the default_collate for `FileTriplet`
    from torch.utils.data._utils.collate import default_collate_fn_map
    default_collate_fn_map[FileTriplet] = lambda batch, *args, **kwargs: batch
except ImportError:
    pass


# ------------------------------ Shard Mode ------------------------------

@dataclass
class SoftShard:
    shard_idx: int | List[int]
    shard_num: int
    subshard: Optional["SoftShard"] = None

    def check_in_shard(self, idx: int) -> bool:
        indices = self.shard_idx
        if isinstance(self.shard_idx, int):
            indices = [self.shard_idx]
        indices = sorted(indices)

        in_shard = False
        lower_cnt = 0

        for i in indices:
            lower_cnt += 1
            if idx % self.shard_num == i:
                in_shard = True
                break

        if not in_shard: return False
        
        if self.subshard is not None:
            return self.subshard.check_in_shard(
                idx // self.shard_num * len(self.shard_idx) + lower_cnt
            )
        else:
            return True


@dataclass
class HardShardMode:
    def get_shard_input(self) -> str:
        raise NotImplementedError("This method should be implemented in a subclass.")

    def get_shard_output(self) -> str:
        raise NotImplementedError("This method should be implemented in a subclass.")


@dataclass
class NoHardShard(HardShardMode):
    input_path: str
    output_path: str

    def get_shard_input(self) -> str:
        return self.input_path

    def get_shard_output(self) -> str:
        return self.output_path


@dataclass
class HardShardModeV1(HardShardMode):
    base_input_path: str
    base_output_path: str
    input_name: str
    output_name: str
    shard_idx: int

    def get_shard_input(self) -> str:
        return os.path.join(self.base_input_path, f"{self.shard_idx}", self.input_name)

    def get_shard_output(self) -> str:
        return os.path.join(self.base_output_path, f"{self.shard_idx}", self.output_name)


# ------------------------------ Input Mode ------------------------------

@dataclass
class InputMode:
    def generate_tasks(self, input_path: str) -> List[dict]:
        raise NotImplementedError("This method should be implemented in a subclass.")

    def to_jsonl(self, input_path: str, jsonl_path: str) -> None:
        tasks = self.generate_tasks(input_path)
        with open(jsonl_path, 'w') as f:
            for task in tasks:
                if "input" in task and isinstance(task["input"], FileTriplet):
                    task.update({"input": task["input"].to_dict()})
                f.write(json.dumps(task) + '\n')


@dataclass
class InputByExts(InputMode):
    exts: list[str]

    def generate_tasks(self, input_path: str) -> List[dict]:
        files = walk_files_of_dir(input_path, self.exts)
        return [
            {
                "input": FileTriplet(
                    path=os.path.join(input_path, file_path, file_name),
                    rel_dir=file_path,
                    file_name=file_name)
            }
            for file_path, file_names in files.items()
            for file_name in file_names
        ]


@dataclass
class InputByGlob(InputMode):
    glob_pattern: str

    def generate_tasks(self, input_path: str) -> List[dict]:
        files = glob.glob(os.path.join(input_path, self.glob_pattern))
        return [
            {
                "input": FileTriplet(
                    path=file,
                    rel_dir=os.path.relpath(os.path.dirname(file), input_path),
                    file_name=os.path.basename(file))
            }
            for file in files
        ]


@dataclass
class InputBySubDirectory(InputMode):
    """
    sub_directory_level: 0 means the input_path itself, 1 means the sub-directories of the input_path, etc.
    """
    sub_directory_level: int

    def generate_tasks(self, input_path: str) -> List[dict]:
        tasks = []
        
        if self.sub_directory_level == 0:
            # Level 0: The input_path itself as a single task
            tasks.append({
                "input": FileTriplet(
                    path=input_path,
                    rel_dir='..',
                    file_name=os.path.basename(os.path.abspath(input_path))
                )
            })
            return tasks

        ret = [input_path]
        for _ in range(self.sub_directory_level):
            new_ret = []
            for dir in ret:
                new_ret.extend([os.path.join(dir, d) for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))])
            ret = new_ret

        for dir in ret:
            tasks.append({
                "input": FileTriplet(
                    path=dir,
                    rel_dir=os.path.relpath(os.path.dirname(dir), input_path),
                    file_name=os.path.basename(dir)
                )
            })
        
        return tasks


@dataclass
class InputFromFileTripletJsonl(InputMode):
    jsonl_path: str

    def generate_tasks(self, input_path: str) -> List[dict]:
        with open(self.jsonl_path, 'r') as f:
            tasks = []
            for line in f:
                data = json.loads(line)
                tasks.append({
                    "input": FileTriplet(
                        path=data["input"]["path"],
                        rel_dir=data["input"]["rel_dir"],
                        file_name=data["input"]["file_name"])
                })
        return tasks


@dataclass
class InputFromWhateverJsonl(InputMode):
    jsonl_path: str

    def generate_tasks(self, input_path: str) -> List[Any]:
        with open(self.jsonl_path, 'r') as f:
            tasks = []
            for line in f:
                data = json.loads(line)
                tasks.append(data)
        return tasks

# ------------------------------ Output Mode ------------------------------

@dataclass
class OutputMode:
    def get_output_params(self, output_path: str, **kwargs) -> dict:
        raise NotImplementedError("This method should be implemented in a subclass.")


@dataclass
class OutputByApendingExt(OutputMode):
    ext: str

    def __init__(self, ext: str) -> None:
        self.ext = ext

    def get_output_params(self, output_path: str, input: FileTriplet, **kwargs) -> dict:
        os.makedirs(os.path.join(output_path, input.rel_dir), exist_ok=True)
        return {
            "output": FileTriplet(
                path=os.path.join(output_path, input.rel_dir, input.file_name + self.ext),
                rel_dir=input.rel_dir,
                file_name=input.file_name + self.ext
            )
        }


@dataclass
class OutputByFilenameSubfoldering(OutputMode):
    file_to_write: dict
    """
    file_to_write: dict, from identifier to real file name. The identifier will be returned by `get_output_params`.
    
    e.g.
    
    file_to_write = {
        "<image>": "image.png",
    }
    
    when `get_output_params` returns, it will return some additional
    
    {
        ...
        "output_<image>": FileTriplet(
            path="path/to/image.png",
            rel_dir="path/to/image",
            file_name="image.png"
        ),
    }
    """

    def get_output_params(self, output_path: str, input: FileTriplet, **kwargs) -> dict:
        os.makedirs(os.path.join(output_path, input.rel_dir, input.file_name), exist_ok=True)
        ret = {
            "output": FileTriplet(
                path=os.path.join(output_path, input.rel_dir, input.file_name),
                rel_dir=input.rel_dir,
                file_name=input.file_name
            )
        }
        for k, v in self.file_to_write.items():
            ret[f"output_{k}"] = FileTriplet(
                path=os.path.join(output_path, input.rel_dir, input.file_name, v),
                rel_dir=os.path.join(input.rel_dir, input.file_name),
                file_name=v
            )
        return ret

# ------------------------------ Finish Check Mode ------------------------------

@dataclass
class FinishCheckMode:
    def is_executed(self, **kwargs) -> bool:
        raise NotImplementedError("This method should be implemented in a subclass.")


@dataclass
class FinishCheckByOutputFileExistence(FinishCheckMode):
    """
    By default, check the existence of `output` file generated by `OutputMode`.
    If provided `output_field_suffix`, check the existence of `output_<output_field_suffix>` file.
    """
    output_field_suffix: Optional[str] = None

    def is_executed(self, output: FileTriplet, **kwargs) -> bool:
        if self.output_field_suffix is None:
            return os.path.exists(output.path)

        return os.path.exists(kwargs[f"output_{self.output_field_suffix}"].path)

