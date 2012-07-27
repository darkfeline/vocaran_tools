#!/usr/bin/env python3

import unittest
import os
import os.path
import shutil
import filecmp
import subprocess

from vocaran_tools.scripts import parse
from vocaran_tools.scripts import dl

TESTDIR = 'fixtures'
TMPDIR = 'tmp'

class TestFiles(unittest.TestCase):

    def setUp(self):
        shutil.copytree(TESTDIR, TMPDIR)
        os.chdir(TMPDIR)

    def test_convert_w_src(self):
        parse.main('src239', 'rank239', 'list')
        self.assertTrue(filecmp.cmp('list', 'list2'))

    def test_convert_wo_src(self):
        parse.main('239', 'rank239', 'list')
        self.assertTrue(filecmp.cmp('list', 'list2'))

    def test_dl_nicosound(self):
        dl.main('-m', 'dl_nicosound', 'list3')
        x = subprocess.call(('md5sum', '-c', 'hash'))
        self.assertTrue(x == 0)

    def tearDown(self):
        os.chdir('..')
        shutil.rmtree(TMPDIR)

if __name__ == "__main__":
    unittest.main()
