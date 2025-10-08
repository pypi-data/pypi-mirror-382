import multiprocessing
import argparse
from tqdm import tqdm


task = None


def _execute(args):
    global task

    if task.is_executed(**args):
        return
    task(**args)


def process(loaded_class, args):
    global task
    parser = argparse.ArgumentParser(description='Kagurazaka MP Backbone.', add_help=False)
    parser.add_argument('--num_process', type=int, default=multiprocessing.cpu_count(), help='Number of processes to use, for normal task (default: number of CPU cores)')
    parser.add_argument('--chunksize', type=int, default=1, help='Number of tasks to be sent to a worker process at a time, for normal task (default: 1)')
    parser.add_argument('-hb', '--help-backbone', action='help', help='Show help message for chosen backbone and exit')
    args, remaining_args = parser.parse_known_args(args)


    task = loaded_class(args=remaining_args)
    # Generate a list of tasks to be executed
    tasks = task.generate_tasks()
    tasks = list(tasks)
    print(f"Generated {len(tasks)} tasks to be executed.")


    pool = multiprocessing.Pool(processes=args.num_process)
    _ = list(tqdm(pool.imap_unordered(_execute, tasks, chunksize=args.chunksize), total=len(tasks)))


    pool.close()
    pool.join()
