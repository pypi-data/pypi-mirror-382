from ..io import HardShardMode, InputMode, OutputMode, SoftShard, FinishCheckMode
from ..mixin import param_mixin, check_placeholder
from typing import Optional


class KagurazakaVanillaTorchMixinV1():
    def load_data(self, **kwargs) -> dict:
        """load more fields for the data, input is the results from input_mode.generate_tasks"""
        raise NotImplementedError("This method should be implemented in a subclass.")


def template_torch_vanilla_v1(
    hard_shard_mode: HardShardMode,
    soft_shard: Optional[SoftShard] = SoftShard(shard_idx=0, shard_num=1),
    input_mode: Optional[InputMode] = None,
    output_mode: Optional[OutputMode] = None,
    finish_check_mode: Optional[FinishCheckMode] = None,
    dataloader: Optional[dict] = None,
    apply: bool = True,
    mixin_mode: bool = True,
):
    from torch.utils.data import Dataset, DataLoader

    def task_class_decorator(cls):

        def internal_mixin_wrapper(mixin):
            # update params
            locals().update(param_mixin({
                "hard_shard_mode": hard_shard_mode,
                "soft_shard": soft_shard,
                "input_mode": input_mode,
                "output_mode": output_mode,
                "finish_check_mode": finish_check_mode,
                "dataloader": dataloader,
            }, mixin))
            assert not check_placeholder({
                "hard_shard_mode": hard_shard_mode,
                "soft_shard": soft_shard,
                "input_mode": input_mode,
                "output_mode": output_mode,
                "finish_check_mode": finish_check_mode,
                "dataloader": dataloader,
            }), "Kagurazaka mixin placeholder found for field, some nasty thing is going to happen!"

            assert not (finish_check_mode is not None and output_mode is None), "finish_check_mode is not None but output_mode is None"

            if input_mode is not None:
                def __get_dataset(self) -> Dataset:
                    class KGDatasetV1(Dataset):
                        def __init__(self_dataset):
                            ret = input_mode.generate_tasks(hard_shard_mode.get_shard_input())
                            if soft_shard is not None:
                                ret = [ret[i] for i in range(len(ret)) if soft_shard.check_in_shard(i)]
                            self_dataset.tasks = ret

                        def __len__(self_dataset):
                            return len(self_dataset.tasks)
                        
                        def __getitem__(self_dataset, idx):
                            extra = self.load_data(**self_dataset.tasks[idx])
                            return {**self_dataset.tasks[idx], **extra}
                    
                    return KGDatasetV1()

                cls.get_dataset = __get_dataset

            if output_mode is not None:
                cls_postprocess_each = cls.postprocess_each

                def __postprocess_each(self, batch_idx, batch_size, **input_batch_and_result) -> None:
                    output_params = output_mode.get_output_params(
                        output_path=hard_shard_mode.get_shard_output(),
                        **input_batch_and_result)
                    cls_postprocess_each(self, batch_idx, batch_size, **input_batch_and_result, **output_params)

                cls.postprocess_each = __postprocess_each

            if finish_check_mode is not None and output_mode is not None:

                def __is_each_executed(self, **kwargs) -> bool:
                    output_params = output_mode.get_output_params(
                        output_path=hard_shard_mode.get_shard_output(), 
                        **kwargs)

                    return finish_check_mode.is_executed(
                        **output_params,
                        **kwargs)

                cls.is_each_executed = __is_each_executed

            if dataloader is not None:
                def __get_dataloader(self) -> DataLoader:
                    return DataLoader(self.get_dataset(), **dataloader)
                cls.get_dataloader = __get_dataloader

            return cls

        return internal_mixin_wrapper if mixin_mode else internal_mixin_wrapper({})

    return task_class_decorator if apply else lambda cls: cls
