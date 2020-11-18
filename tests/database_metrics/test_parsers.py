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
        test_metrics = (b'count(*)\n1604\n',
                        b'db\tsize_mb\nepidata\t7.79687500\ninformation_schema\t0.18750000\n',
                        1,
                        [{"memory_stats": {"usage": 3}}, {"memory_stats": {"usage": 4}}])
        self.assertDictEqual(
            parse_metrics(test_metrics),
            {"table_rows": 1604,
             "db_disk_usage_mb": 7.796875,
             "runtime": 1,
             "memory_usage_mb": 4/1024/1024}
        )
