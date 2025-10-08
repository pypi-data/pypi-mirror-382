from ..io import HardShardMode, InputMode, OutputMode, SoftShard, FinishCheckMode
from ..mixin import param_mixin, check_placeholder
from typing import Optional


def template_normal(
    hard_shard_mode: HardShardMode,
    soft_shard: Optional[SoftShard] = SoftShard(shard_idx=0, shard_num=1),
    input_mode: Optional[InputMode] = None,
    output_mode: Optional[OutputMode] = None,
    finish_check_mode: Optional[FinishCheckMode] = None,
    apply: bool = True,
    mixin_mode: bool = True,
):
    def task_class_decorator(cls):

        def internal_mixin_wrapper(mixin):
            # update params
            locals().update(param_mixin({
                "hard_shard_mode": hard_shard_mode,
                "soft_shard": soft_shard,
                "input_mode": input_mode,
                "output_mode": output_mode,
                "finish_check_mode": finish_check_mode,
            }, mixin))
            assert not check_placeholder({
                "hard_shard_mode": hard_shard_mode,
                "soft_shard": soft_shard,
                "input_mode": input_mode,
                "output_mode": output_mode,
                "finish_check_mode": finish_check_mode,
            }), "Kagurazaka mixin placeholder found for field, some nasty thing is going to happen!"

            assert not (finish_check_mode is not None and output_mode is None), "finish_check_mode is not None but output_mode is None"

            # get the original methods
            cls_generate_tasks = cls.generate_tasks
            cls_process = cls.process
            cls_is_executed = cls.is_executed

            def __generate_tasks(self) -> list:
                if input_mode is not None:
                    ret = input_mode.generate_tasks(hard_shard_mode.get_shard_input())
                else:
                    ret = cls_generate_tasks(self)
                if soft_shard is not None:
                    ret = [ret[i] for i in range(len(ret)) if soft_shard.check_in_shard(i)]
                return ret

            def __process(self, **kwargs) -> None:
                if output_mode is not None:
                    output_params = output_mode.get_output_params(
                        output_path=hard_shard_mode.get_shard_output(),
                        **kwargs)
                    cls_process(self, **kwargs, **output_params)
                else:
                    cls_process(self, **kwargs)

            def __is_executed(self, **kwargs) -> bool:
                if finish_check_mode is None or output_mode is None:
                    return cls_is_executed(self, **kwargs)

                output_params = output_mode.get_output_params(
                    output_path=hard_shard_mode.get_shard_output(), 
                    **kwargs)
                return finish_check_mode.is_executed(
                    **output_params,
                    **kwargs)


            cls.generate_tasks = __generate_tasks
            cls.process = __process
            cls.is_executed = __is_executed
            
            return cls

        return internal_mixin_wrapper if mixin_mode else internal_mixin_wrapper({})

    return task_class_decorator if apply else lambda cls: cls

