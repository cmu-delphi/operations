"""Unit tests for disk_usage_checker.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.operations.disk_usage_checker'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def setUp(self):
    self.df_command = MagicMock()
    self.df_command.run.return_value = (
      'Filesystem  Size  Used Avail Use% Mounted on\n'
      '/dev/sda1   477M  168M  281M  38% /home\n'
      '/dev/sdb2   100M   90M   10M  90% /mnt/shared\n'
    )
    self.checker = DiskUsageChecker(self.df_command)

  def test_get_argument_parser(self):
    """An ArgumentParser should be returned."""
    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  def test_validate_args(self):
    """Arguments should be validated."""

    with self.subTest(name='negative limit'):
      with self.assertRaises(InvalidArgsException):
        validate_args(MagicMock(limit=-1))

    with self.subTest(name='huge limit'):
      with self.assertRaises(InvalidArgsException):
        validate_args(MagicMock(limit=101))

    with self.subTest(name='valid limit'):
      self.assertEqual(validate_args(MagicMock(limit=75)), (75,))

  def test_disk_usage_checker_new_instance(self):
    """Acquire a production-ready instance."""
    self.assertIsInstance(DiskUsageChecker.new_instance(), DiskUsageChecker)

  def test_check_all(self):
    """Test all combinations of usage scenarios."""

    with self.subTest(name='all under'):
      text, result = self.checker.check_all(97)
      self.assertTrue(result)

    with self.subTest(name='mixed'):
      text, result = self.checker.check_all(50)
      self.assertFalse(result)

    with self.subTest(name='all over'):
      text, result = self.checker.check_all(20)
      self.assertFalse(result)

  def test_raise_if_any_over_limit(self):
    """Raise when the limit is exceeded."""

    with self.subTest(name='check pass'):
      self.assertIsNone(self.checker.raise_if_exceeds(95))

    with self.subTest(name='check fail'):
      with self.assertRaises(DiskUsageException):
        self.checker.raise_if_exceeds(50)
