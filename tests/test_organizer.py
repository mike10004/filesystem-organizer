import os
import shutil
import os.path
import unittest
import tempfile
import organizer
import tests
from organizer import Subdivider


tests.configure_logging()


def _create_file(pathname, binary_data=None):
    with open(pathname, 'wb') as ofile:
        if binary_data:
            ofile.write(binary_data)
    assert os.path.isfile(pathname)


class TestSubdivider(unittest.TestCase):


    def assertFileContains(self, pathname, bindata):
        fnf, actual = None, None
        try:
            with open(pathname, 'rb') as ifile:
                actual = ifile.read()
        except FileNotFoundError as e:
            fnf = f"could not open {pathname} due to FileNotFoundError {e}"
        if fnf:
            self.fail(fnf)
        self.assertEqual(bindata, actual, f"data from {pathname}")

    def test_subdivide(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = os.path.join(tmpdir, 'source')
            os.makedirs(source_dir)
            FILES = "abcdefghij"
            contents = {}
            for fn in FILES:
                data =fn.encode('utf-8')
                _create_file(os.path.join(source_dir, fn), data)
                contents[fn] = data
            subdivider = Subdivider()
            subdivider.subdivide_max_files(source_dir, 3)
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
