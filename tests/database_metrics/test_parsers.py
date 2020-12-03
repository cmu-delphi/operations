"""Tests for parsers.py"""
import unittest

# py3tester coverage target
__test_target__ = 'delphi.operations.database_metrics.parsers'


class TestParser(unittest.TestCase):

    def test_parse_db_size(self):
        test_query_result = b'db\tsize_mb\nepidata\t7.79687500\ninformation_schema\t0.18750000\n'
        self.assertEqual(parse_db_size(test_query_result), 7.796875)

    def test_parse_db_rows(self):
        test_query_result = b'count(*)\n1604\n'
        self.assertEqual(parse_row_count(test_query_result), 1604)

    def test_metrics(self):
        test_metrics = (100.5,
                        120,
                        10,
                        25,
                        1,
                        [{"memory_stats": {"usage": 3}}, {"memory_stats": {"usage": 4}}])
        self.assertDictEqual(
            parse_metrics(test_metrics),
            {"final_table_rows": 25,
             "rows_loaded": 15,
             "db_size_mb": 120,
             "size_loaded_mb": 19.5,
             "runtime": 1,
             "peak_memory_mb": 4/1024/1024}
        )
