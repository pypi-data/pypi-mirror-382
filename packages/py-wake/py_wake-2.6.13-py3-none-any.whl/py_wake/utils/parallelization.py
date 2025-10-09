import multiprocessing
import atexit
import platform
import gc
from itertools import starmap

pool_dict = {}


def get_pool(processes=multiprocessing.cpu_count()):
    if processes not in pool_dict:
        # close pools
        for pool in pool_dict.values():
            pool.close()
        pool_dict.clear()

        if platform.system() == 'Darwin':  # pragma: no cover
            pool_dict[processes] = multiprocessing.get_context('fork').Pool(processes)
        else:
            pool_dict[processes] = multiprocessing.Pool(processes)
    return pool_dict[processes]


class gc_func():
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        r = self.func(*args, **kwargs)
        gc.collect()
        return r


def get_pool_map(processes=multiprocessing.cpu_count()):
    pool = get_pool(processes)

    def gc_map(func, iterable, chunksize=None):
        return pool.map(gc_func(func), iterable, chunksize)
    return gc_map


def get_pool_starmap(processes=multiprocessing.cpu_count()):
    pool = get_pool(processes)

    def gc_map(func, iterable, chunksize=None):
        return pool.starmap(gc_func(func), iterable, chunksize)
    return gc_map


def close_pools():  # pragma: no cover
    for k, pool in pool_dict.items():
        pool.close()


def get_map_func(n_cpu, verbose, desc='', unit='it'):
    n_cpu = n_cpu or multiprocessing.cpu_count()
    if n_cpu > 1:
        map_func = get_pool_map(n_cpu)
    else:
        from tqdm import tqdm

        def map_func(f, iter):
            return tqdm(map(f, iter), desc=desc, unit=unit, total=len(iter), disable=not verbose)
    return map_func


def get_starmap_func(n_cpu, verbose, desc='', unit='it', leave=True):
    n_cpu = n_cpu or multiprocessing.cpu_count()
    if n_cpu > 1:
        map_func = get_pool_starmap(n_cpu)
    else:
        from tqdm import tqdm

        def map_func(f, iter):
            return starmap(f, tqdm(iter, desc=desc, unit=unit, total=len(iter), disable=not verbose, leave=leave))
    return map_func


atexit.register(close_pools)
