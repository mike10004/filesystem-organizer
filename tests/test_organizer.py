import os
import io
import os.path
import logging
import unittest
import tempfile
import organizer
import tests
from organizer import Subdivider


_log = logging.getLogger(__name__)
tests.configure_logging()


def _create_file(pathname, binary_data=None):
    with open(pathname, 'wb') as ofile:
        if binary_data:
            ofile.write(binary_data)
    assert os.path.isfile(pathname)


class CountingMeter(organizer.ProgressMeter):

    def __init__(self, increment):
        self.buffer = io.StringIO()
        super(CountingMeter, self).__init__(increment, self.buffer)
        self.num_reports = 0

    def report(self, num_moved, num_expected):
        super().report(num_moved, num_expected)
        self.num_reports += 1

    def text(self):
        return self.buffer.getvalue()



class TestSubdivider(unittest.TestCase):


    def assertFileContains(self, pathname, bindata):
        fnf, actual = None, None
        try:
            with open(pathname, 'rb') as ifile:
                actual = ifile.read()
        except FileNotFoundError:
            fnf = f"could not open {pathname} due to FileNotFoundError"
        if fnf:
            self.fail(fnf)
        self.assertEqual(bindata, actual, f"data from {pathname}")

    def test_subdivide_progress(self):
        nfiles = 100
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = os.path.join(tmpdir, 'source')
            os.makedirs(source_dir)
            for i in range(nfiles):
                _create_file(os.path.join(source_dir, 'f' + str(i + 1)))
            subdivider = Subdivider()
            report_increment = 17
            expected_reports = nfiles // report_increment
            subdivider.callback = CountingMeter(report_increment)
            subdivider.subdivide_max_files(source_dir, 12)
        self.assertEqual(expected_reports, subdivider.callback.num_reports, "expected reports")
        text = subdivider.callback.text()
        lines = [line.strip() for line in text.split("\n")]
        lines = list(filter(lambda x: x, lines))
        self.assertNotEqual(0, lines)
        _log.debug("%d lines in output", len(lines))


    def test_subdivide(self):
        FILES = "abcdefghij"
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = os.path.join(tmpdir, 'source')
            os.makedirs(source_dir)
            contents = {}
            for fn in FILES:
                data = fn.encode('utf-8')
                _create_file(os.path.join(source_dir, fn), data)
                contents[fn] = data
            subdivider = Subdivider()
            subdivider.format_width = 2
            num_moved = subdivider.subdivide_max_files(source_dir, 3)
            self.assertFileContains(os.path.join(source_dir, "00", "a"), contents["a"])
            self.assertFileContains(os.path.join(source_dir, "00", "b"), contents["b"])
            self.assertFileContains(os.path.join(source_dir, "00", "c"), contents["c"])
            self.assertFileContains(os.path.join(source_dir, "01", "d"), contents["d"])
            self.assertFileContains(os.path.join(source_dir, "01", "e"), contents["e"])
            self.assertFileContains(os.path.join(source_dir, "01", "f"), contents["f"])
            self.assertFileContains(os.path.join(source_dir, "02", "g"), contents["g"])
            self.assertFileContains(os.path.join(source_dir, "02", "h"), contents["h"])
            self.assertFileContains(os.path.join(source_dir, "02", "i"), contents["i"])
            self.assertFileContains(os.path.join(source_dir, "03", "j"), contents["j"])
        self.assertEqual(len(FILES), num_moved, "num_moved")


class TestModuleMethods(unittest.TestCase):

    def test_default_namer(self):
        namer = organizer.default_namer(None, 202599 / 1024)
        names = [namer.__next__() for _ in range(198)]
        self.assertEqual('000', names[0])
        self.assertEqual('197', names[-1])
