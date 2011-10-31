#!/usr/bin/env python
from __future__ import with_statement

import doctest
import os
import shutil
import unittest
import tempfile
import textwrap
import mashed_potato

get_paths_from_configuration = mashed_potato.get_paths_from_configuration
path_matches_regexps = mashed_potato.path_matches_regexps

class MinifyTest(unittest.TestCase):
    FIXTURES = {
        "test.js": """
var a = null;
function foo(bar) {
  console.log("baz");
  return bar;
}""",
        "test.css": """
body {
  width: 100%;
  margin: 0px 0px 0px 0px;
}"""
        }

    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.file_paths = []
        for filename, contents in self.FIXTURES.items():
            file_path = os.path.join(self._temp_dir, filename)
            fh = open(file_path, "w")
            fh.write(contents)
            self.file_paths.append(file_path)

    def test_minify_files_individually(self):
        for file_path in self.file_paths:
            mashed_potato.minify(file_path)
            minified_name = mashed_potato.get_minified_name(file_path)
            self.assertTrue(os.path.exists(minified_name))

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

class ConfigurationTest(unittest.TestCase):
    def test_comments_ignored(self):
        path_regexps = get_paths_from_configuration("/", "# foo \n# bar")
        self.assertEqual(path_regexps, [])

    def test_blank_lines_ignored(self):
        path_regexps = get_paths_from_configuration("/", "# \n # ")
        self.assertEqual(path_regexps, [])

    def test_regexp_number(self):
        path_regexps = get_paths_from_configuration("/", "foo\nbar\nbaz")
        self.assertEqual(len(path_regexps), 3)


class RegexpMatchingTest(unittest.TestCase):
    def test_simple_regexp(self):
        path_regexps = get_paths_from_configuration("/", "foo")
        self.assertTrue(path_matches_regexps("/foo", path_regexps))

    def test_complex_regexp(self):
        path_regexps = get_paths_from_configuration("/", "abc/[^/]+/ghi")
        self.assertTrue(path_matches_regexps("/abc/def/ghi", path_regexps))

#Make doctests discoverable by unittest
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(mashed_potato))
    return tests

if __name__ == '__main__':
    unittest.main()
    doctest.testfile('mashed_potato.py')
