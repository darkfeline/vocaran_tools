#!/usr/bin/env python3

import unittest
import os
import os.path
import shutil
import filecmp

import parse

TESTDIR = 'test'
TMPDIR = 'tmp'

class TestParse(unittest.TestCase):

    def setUp(self):
        shutil.copytree(TESTDIR, TMPDIR)
        self.files = {}
        for f in os.listdir(TMPDIR):
            self.files[f] = os.path.join(TMPDIR, f)

    def test_convert_w_src(self):
        parse.main(self.files['src239'], self.files['rank239'],
                self.files['list'])
        self.assertTrue(filecmp.cmp(self.files['list'], self.files['list2']))

    def test_convert_wo_src(self):
        parse.main('239', self.files['rank239'], self.files['list'])
        self.assertTrue(filecmp.cmp(self.files['list'], self.files['list2']))

    def tearDown(self):
        shutil.rmtree(TMPDIR)

if __name__ == "__main__":
    unittest.main()
