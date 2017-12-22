"""Unit tests for secrets.py."""

# standard library
import ast
import inspect
import itertools
import re
import unittest

# first party
from delphi.operations.environment import Environment

# py3tester coverage target
__test_target__ = 'delphi.operations.secrets'


class SanityChecks(unittest.TestCase):
  """Makes sure everything looks normal."""

  def test_no_actual_secrets(self):
    # re-import the module to get a top-level handle
    import delphi.operations.secrets as secrets

    # get the abstract syntax tree
    tree = ast.parse(inspect.getsource(secrets))

    # helper to filer the abstract syntax tree by type
    def get_elements(type_, root=tree):
      return [node for node in ast.walk(root) if isinstance(node, type_)]

    # there should be no functions...
    self.assertEqual(len(get_elements(ast.FunctionDef)), 0)

    # ...nor async functions (python 3.5+)
    if hasattr(ast, 'AsyncFunctionDef'):
      self.assertEqual(len(get_elements(ast.AsyncFunctionDef)), 0)

    # find all assignments
    assign_nodes = get_elements(ast.Assign)

    # find strings within assignments
    string_nodes = [get_elements(ast.Str, a) for a in assign_nodes]
    strings = [node.s for node in itertools.chain.from_iterable(string_nodes)]

    # check each secret
    pattern = re.compile('{SECRET_\\S+}')
    for secret in strings:
      with self.subTest(secret=secret):
        if Environment.is_prod():
          # all strings should be substituted
          self.assertIsNone(pattern.match(secret), 'secret may be unavailable')
        else:
          # all strings should be placeholders
          self.assertIsNotNone(pattern.match(secret), 'secret may be exposed')
