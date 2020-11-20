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
            {"test": "output1"},
            {"test": "output2"},
            {"test": "output3"},
            {"test": "output4"},
            {"test": "output5"},
            {"test": "output6"}
        ]
        expected = {
            "datasets": [("a", "b"), ("c", "d")],
            "append_datasets": False,
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
        output = monitor.measure_database([("a", "b"), ("c", "d")], None, None, ["q1"])
        self.assertDictEqual(output, expected)
        self.assertEqual(mock_clear.call_count, 2)
