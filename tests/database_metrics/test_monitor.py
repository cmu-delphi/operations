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
            {"a": 1, "b": 2., "c": 3, "d": 4},
            {"a": 5, "b": 6., "c": 7, "d": 8},
            {"a": 9, "b": 10., "c": 11, "d": 12},
            {"a": 2, "b": 4., "c": 6, "d": 8},
            {"a": 1, "b": 3., "c": 5, "d": 7},
            {"a": 3, "b": 6., "c": 9, "d": 12},
        ]
        expected = {
            "datasets": [("a", "b"), ("c", "d")],
            "append_datasets": False,
            "load": [
                {"a": 1, "b": 2., "c": 3, "d": 4},
                {"a": 2, "b": 4., "c": 6, "d": 8}
            ],
            "meta": [
                {"a": 5, "b": 6., "c": 7, "d": 8},
                {"a": 1, "b": 3., "c": 5, "d": 7}
            ],
            "query0": [
                {"a": 9, "b": 10., "c": 11, "d": 12},
                {"a": 3, "b": 6., "c": 9, "d": 12}
            ],
        }
        output = monitor.measure_database([("a", "b"), ("c", "d")], None, None, ["q1"])
        self.assertDictEqual(output, expected)
        self.assertEqual(mock_clear.call_count, 2)
