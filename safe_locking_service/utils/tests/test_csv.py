import unittest
from io import StringIO

from .. import csv_helper


class CSVTestCase(unittest.TestCase):
    def test_parsing(self):
        csv_content = "name,age\nJohn,30\nJane,25"
        with StringIO(csv_content) as file:
            result = list(csv_helper.parse(file))

            assert result == [["John", "30"], ["Jane", "25"]]

    def test_no_rows(self):
        csv_content = "name,age"
        with StringIO(csv_content) as file:
            result = list(csv_helper.parse(file))

            assert result == []

    def test_no_header_skip(self):
        csv_content = "name,age\nJohn,30\nJane,25"
        with StringIO(csv_content) as file:
            result = list(csv_helper.parse(file, skip_header=False))

            assert result == [["name", "age"], ["John", "30"], ["Jane", "25"]]
