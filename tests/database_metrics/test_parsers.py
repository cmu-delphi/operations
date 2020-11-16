"""Tests for parsers.py"""
from src.database_metrics import parsers


class TestParser:

    def test_parse_db_size(self):
        test_query_result = b'db\tsize_mb\nepidata\t7.79687500\ninformation_schema\t0.18750000\n'
        assert parsers.parse_db_size(test_query_result) == 7.796875

    def test_metrics(self):
        test_metrics = (1,
                        2,
                        [{"memory_stats": {"usage": 3}}, {"memory_stats": {"usage": 4}}])
        assert parsers.parse_metrics(test_metrics) == {
            "db_disk_usage_mb": 1,
            "runtime": 2,
            "memory_usage_mb": [3/1024/1024, 4/1024/1024]}
