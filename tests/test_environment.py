"""Unit tests for environment.py."""

# standard library
import unittest

# py3tester coverage target
__test_target__ = 'delphi.operations.environment'


class FunctionTests(unittest.TestCase):
  """Tests each function individually."""

  def test_is_prod(self):
    # the value doesn't matter as long as it's a boolean
    self.assertTrue(isinstance(Environment.is_prod(), bool))
