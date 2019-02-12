# organizer module

import os
import os.path
import shutil
import logging
from typing import Iterator


_log = logging.getLogger(__name__)


def default_namer(expected_max: int=None) -> Iterator[str]:
    if expected_max is None:
        expected_max = 0
    n = 0
    fmt = "{:0" + str(len(str(expected_max))) + "d}"
    while True:
        yield fmt.format(n)
        n += 1


class Subdivider(object):

    filter = None

    def subdivide_max_files(self, directory: str, max_files_per_dir: int, dest_root:str=None):
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
            return
        namer = default_namer(num_files)
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


