from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from sys import modules
from threading import active_count
from typing import Callable, List

from tqdm import tqdm

from .logging import logger

__all__ = ['multi_process_thread']


def process_worker_wrapper(args):
    _args = (args[0], [args[1]]) if not isinstance(args[1], list) else args
    return _args[0](*_args[1])


def multi_process_thread(
    func: Callable,
    mpargs: List,
    nprocess: int = -1,
    pool_func: str = 'Pool',
    map_func: str = 'imap',
    progress_bar: bool = True,
    progress_desc: str = None,
) -> List:
    """
    Create process / thread pool

    @param func: process / thread function
    @param kwargs: process / thread keyword argument list
    @param nprocess: number of process / thread
    @param pool_func: [Pool(multi process), ThreadPoolExecutor(multi thread)]
    @param map_func: [map, imap]
    """
    if nprocess == -1:
        if pool_func == 'Pool':
            nprocess = cpu_count()
        if pool_func == 'ThreadPoolExecutor':
            nprocess = active_count()

    assert nprocess > 0, f'invalid process num {nprocess}'
    if nprocess > 1:
        logger.debug(f'multi {"process" if pool_func == "Pool" else "thread"} with proc {nprocess}')
        with getattr(modules[__name__], pool_func)(nprocess) as pool:
            return list(tqdm(getattr(pool, map_func)(
                process_worker_wrapper, [(func, args) for args in mpargs]),
                total=len(mpargs), desc=progress_desc, disable=(not progress_bar)))
    else:
        return list([func(*(args if isinstance(args, list) else [args]))
            for args in tqdm(mpargs, desc=progress_desc, disable=(not progress_bar))])
