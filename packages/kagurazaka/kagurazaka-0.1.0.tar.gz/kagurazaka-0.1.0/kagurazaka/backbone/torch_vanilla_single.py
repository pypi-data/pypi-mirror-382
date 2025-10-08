from tqdm import tqdm
import argparse


def process(loaded_class, args):
    import torch

    if not torch.cuda.is_available():
        raise ValueError("CUDA is not available.")

    parser = argparse.ArgumentParser(description='Kagurazaka Torch Vanilla Single GPU Backbone.', add_help=False)
    parser.add_argument('--device', type=str, default='cuda', help='The device to use')
    parser.add_argument('-hb', '--help-backbone', action='help', help='Show help message for chosen backbone and exit')
    args, remaining_args = parser.parse_known_args(args)

    task = loaded_class(args=remaining_args)

    task.load_model(args.device)
    dataloader = task.get_dataloader()

    for batch in tqdm(dataloader):
        if task.is_executed(batch):
            continue
        task(device=args.device, batch=batch)
