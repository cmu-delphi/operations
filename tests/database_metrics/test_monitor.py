"""Tests for monitor.py"""
import unittest
from unittest.mock import patch, MagicMock

from delphi.operations.database_metrics import monitor

# py3tester coverage target
__test_target__ = 'delphi.operations.database_metrics.monitor'


class TestMonitor(unittest.TestCase):

    @patch("delphi.operations.database_metrics.monitor._clear_db")
    @patch("delphi.operations.database_metrics.monitor.parse_metrics")
    @patch("delphi.operations.database_metrics.monitor.get_metrics")
    def test_measure_database(self, mock_metrics, mock_parser, mock_clear):
        # mock_container = MagicMock()
        # mock_container.exec_run.return_value = None
        # mock_docker_client = MagicMock()
        # mock_docker_client.containers.run.return_value = mock_container

        mock_metrics.return_value = None
        mock_clear.return_value = None
        mock_parser.side_effect = [
            {"table_rows": 1, "db_disk_usage_mb": 2., "runtime": 3, "memory_usage_mb": 4},
            {"table_rows": 5, "db_disk_usage_mb": 6., "runtime": 7, "memory_usage_mb": 8},
            {"table_rows": 9, "db_disk_usage_mb": 10., "runtime": 11, "memory_usage_mb": 12},
        ]
        expected = {
            "datasets": [("a", "b")],
            "append_datasets": False,
            "load": [
                {"table_rows": 1, "db_disk_usage_mb": 2., "runtime": 3, "memory_usage_mb": 4}
            ],
            "meta": [
                {"table_rows": 5, "db_disk_usage_mb": 6., "runtime": 7, "memory_usage_mb": 8}
            ],
            "query0": [
                {"table_rows": 9, "db_disk_usage_mb": 10., "runtime": 11, "memory_usage_mb": 12}
            ],
        }
        output = monitor.measure_database([("a", "b")], None, None, ["q1"])
        self.assertDictEqual(output, expected)
        mock_clear.assert_called_once()
