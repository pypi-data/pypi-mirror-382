from __future__ import annotations

import importlib
import sys
from contextlib import contextmanager
from cProfile import Profile
from pstats import SortKey, Stats


@contextmanager
def profiled():
    with Profile() as profiler:
        yield
        stats = Stats(profiler)
        stats.sort_stats(SortKey.CUMULATIVE)
        stats.print_stats()
        stats.dump_stats("profile")


def load_code():
    if "tests.data.code" in sys.modules:
        del sys.modules["tests.data.code"]
    return importlib.import_module("tests.data.code")


def import_via_file_path(module_name: str, file_path: str):
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
