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
        mock_client = MagicMock()
        mock_client.containers.get.return_value = None
        mock_metrics.return_value = None
        mock_clear.return_value = None
        mock_parser.side_effect = [
            {"test": "output1"},
            {"test": "output2"},
            {"test": "output3"},
            {"test": "output4"},
            {"test": "output5"},
            {"test": "output6"}
        ]
        test_datasets = [("a", "b"), ("c", "d")]
        test_queries = ["q0"]
        expected = {
            "datasets": test_datasets,
            "append_datasets": False,
            "queries": test_queries,
            "load": [
                {"test": "output1"},
                {"test": "output4"},
            ],
            "meta": [
                {"test": "output2"},
                {"test": "output5"},
            ],
            "query0": [
                {"test": "output3"},
                {"test": "output6"},
            ],
        }
        output = monitor.measure_database(test_datasets, mock_client, "container", "image", test_queries)
        self.assertDictEqual(output, expected)
        self.assertEqual(mock_clear.call_count, 2)
