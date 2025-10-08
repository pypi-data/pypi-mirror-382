try:
    import torch
    from torch.utils.data import Dataset, DataLoader
except ImportError:
    # make torch a dummy class
    # so that the code can be run without torch
    print("Warning: torch is not installed. Partial features are unavailable.")
    class torch:
        class Tensor:
            pass
    class Dataset:
        pass
    class DataLoader:
        pass


class KagurazakaVanillaTorchTaskV1():
    def __init__(self, args) -> None:
        """
        Initialize the task with command line arguments
        args can be passed to ArgumentParser.parse_args() to parse remaining command line arguments.
        """
        pass

    # ------------------------------ Model / Dataloader ------------------------------
    def load_model(self, device) -> None:
        """Load the model on a device."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def get_dataset(self) -> Dataset:
        """Return a Dataset object."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def get_dataloader(self) -> DataLoader:
        """Get Dataloader object."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    # ------------------------------ Bookkeeping ------------------------------
    def is_each_executed(self, **kwargs) -> bool:
        """Check if the task has already been executed for each element in the batch."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def is_executed(self, batch) -> bool:
        """Check if the task has already been executed."""
        # get keys of batch
        keys = list(batch.keys())
        bs = len(batch[keys[0]])
        return all(self.is_each_executed(**{key: batch[key][i] for key in keys}) for i in range(bs))

    # ------------------------------ Process ------------------------------
    def inference(self, device, batch_size, **batch) -> torch.Tensor | dict | list:
        """Inference the batch. Return a tensor of shape (batch_dim, *)."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def postprocess_each(self, batch_idx, batch_size, **input_batch_and_result) -> None:
        """
        Postprocess each element in the batch.
        `kwargs` should include all fields in `result`, `input_batch`.
        if `result` is a tensor or a list, the field name should just be `result`.
        """
        raise NotImplementedError("This method should be implemented in a subclass.")

    def postprocess(self, batch_size, results, **batch) -> None:
        """Postprocess the inference result."""
        if isinstance(results, torch.Tensor) or isinstance(results, list):
            for i in range(batch_size):
                self.postprocess_each(i, batch_size, **{key: batch[key][i] for key in batch.keys()}, result=results[i])
        elif isinstance(results, dict):
            for i in range(batch_size):
                self.postprocess_each(i, batch_size, **{key: batch[key][i] for key in batch.keys()}, **{key: results[key][i] for key in results.keys()})

    def process(self, device, batch) -> None:
        """Process the task."""
        batch_size = len(batch[list(batch.keys())[0]])
        res = self.inference(device, batch_size, **batch)
        self.postprocess(batch_size, res, **batch)

    def __call__(self, device, batch) -> None:
        self.process(device, batch)
