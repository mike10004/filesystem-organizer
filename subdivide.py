#!/usr/bin/env python

import os
import os.path
import logging
import argparse
import organizer


_DEFAULT_MAX_FILES = 1024
_log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", metavar="ROOT", nargs="?", default=os.getcwd(), help="directory to subdivide")
    parser.add_argument("--max-files", type=int, metavar="N", help="set max number of files per subdirectory")
    parser.add_argument("--destination", metavar="DIR", help="set destination; default is ROOT")
    parser.add_argument("--log-level", "-l", metavar="LEVEL", choices=('DEBUG', 'INFO', 'WARN', 'ERROR'), default='INFO', help="set log level")
    parser.add_argument("--progress", type=int, metavar="N", help="report progress at increments of N")
    args = parser.parse_args()
    logging.basicConfig(level=logging.__dict__[args.log_level])
    subdivider = organizer.Subdivider()
    if args.progress:
        subdivider.callback = organizer.ProgressMeter(args.progress)
    max_files = _DEFAULT_MAX_FILES
    if args.max_files is not None:
        max_files = args.max_files
    if max_files <= 0:
        parser.error("max files must be positive integer")
    subdivider.subdivide_max_files(args.directory, max_files)
    return 0


if __name__ == '__main__':
    exit(main())
