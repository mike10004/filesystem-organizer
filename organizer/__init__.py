# organizer module

import os
import sys
import math
import os.path
import shutil
import logging
from typing import Iterator, Callable


_log = logging.getLogger(__name__)


def default_namer(fmt_width: int=None, expected_max: float=None) -> Iterator[str]:
    if fmt_width is None:
        if expected_max is None:
            expected_max = 0
        else:
            expected_max = int(math.ceil(expected_max))
        fmt_width = len(str(expected_max))
    n = 0
    fmt = "{:0" + str(fmt_width) + "d}"
    while True:
        yield fmt.format(n)
        n += 1


class Subdivider(object):

    format_width: int = None
    filter: Callable = None
    callback: Callable = None

    def subdivide_max_files(self, directory: str, max_files_per_dir: int, dest_root:str=None) -> int:
        _log.debug("subdividing %s with %d files per dir", directory, max_files_per_dir)
        assert max_files_per_dir > 0, "max files per dir must be positive integer"
        dest_root = dest_root or directory
        src_filenames = tuple()
        for root, dirs, files in os.walk(directory):
            src_filenames = files
        if self.filter is not None:
            src_filenames = list(filter(self.filter, src_filenames))
        src_filenames = sorted(src_filenames)
        num_files = len(src_filenames)
        _log.debug("directory has %d files", num_files)
        if not num_files:
            return 0
        namer = default_namer(self.format_width, expected_max=num_files/max_files_per_dir)
        subdir_num_files = 0
        num_moved = 0
        current_subdir_name = namer.__next__()
        os.makedirs(os.path.join(dest_root, current_subdir_name), exist_ok=True)
        for filename in src_filenames:
            if subdir_num_files >= max_files_per_dir:
                current_subdir_name = namer.__next__()
                os.makedirs(os.path.join(dest_root, current_subdir_name), exist_ok=True)
                subdir_num_files = 0
            dest_path = os.path.join(dest_root, current_subdir_name, filename)
            shutil.move(os.path.join(directory, filename), dest_path)
            subdir_num_files += 1
            num_moved += 1
            _log.debug("%d/%d: moved %s to %s", subdir_num_files, num_moved, filename, os.path.dirname(dest_path))
            self._invoke_callback(num_moved, num_files)
        return num_files

    def _invoke_callback(self, num_moved, num_expected):
        if self.callback is not None:
            try:
                self.callback(num_moved, num_expected)
            except TypeError as e:
                _log.info("error invoking callback: %s", e)


class ProgressMeter(object):

    def __init__(self, increment, ofile=sys.stderr):
        self.increment = increment
        self.ofile = ofile

    def report(self, num_moved, num_expected):
        print("progress out of", num_expected, ":", num_moved, file=self.ofile)

    def __call__(self, *args, **kwargs):
        num_moved, num_expected = args[0], args[1]
        if num_moved % self.increment == 0:
            self.report(num_moved, num_expected)


