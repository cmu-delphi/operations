"""Unit tests for adduser.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.operations.adduser'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def setUp(self):
    pass

  def test_get_argument_parser(self):
    """An ArgumentParser should be returned."""
    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  def test_validate_args(self):
    """Arguments should be validated."""

    with self.subTest(name='username too short'):
      with self.assertRaises(AccountCreationException):
        validate_args(MagicMock(username='df'))

    with self.subTest(name='username starts with number'):
      with self.assertRaises(AccountCreationException):
        validate_args(MagicMock(username='0abcdef'))

    with self.subTest(name='username not alphanumeric'):
      with self.assertRaises(AccountCreationException):
        validate_args(MagicMock(username='x1y2-3'))

    with self.subTest(name='obviously not an email'):
      with self.assertRaises(AccountCreationException):
        validate_args(MagicMock(username='username', email='nothing'))

    with self.subTest(name='valid arguments'):
      args = MagicMock(username='user', firstname='fn', email='x@y.z')
      self.assertEqual(validate_args(args), ('user', 'fn', 'x@y.z'))

  def test_adduser_new_instance(self):
    """Acquire a production-ready instance."""
    self.assertIsInstance(AddUser.new_instance(), AddUser)

  def test_shell_command_interpolates_arguments(self):
    """Shell commands are executed with the given arguments."""
    subprocess = MagicMock()
    subprocess.check_output.return_value = b'abc'
    adduser = AddUser(None, subprocess, None)

    adduser._shell_command('ls %s %d %.3f', 'x', 5, 3.14159)

    self.assertEqual(subprocess.check_output.call_count, 1)
    args, kwargs = subprocess.check_output.call_args
    self.assertEqual(args, ('ls x 5 3.142',))

  def test_shell_command_uses_shell_semantics(self):
    """Shell commands are executed with shell semantics."""
    subprocess = MagicMock()
    subprocess.check_output.return_value = b'abc'
    adduser = AddUser(None, subprocess, None)

    adduser._shell_command('some command')

    self.assertEqual(subprocess.check_output.call_count, 1)
    args, kwargs = subprocess.check_output.call_args
    self.assertEqual(kwargs, {'shell': True})

  def test_shell_command_casts_output_as_string(self):
    """Shell command output is interpreted as a string."""
    subprocess = MagicMock()
    subprocess.check_output.return_value = b'abc'
    adduser = AddUser(None, subprocess, None)

    result = adduser._shell_command('some command')

    self.assertEqual(subprocess.check_output.call_count, 1)
    self.assertIsInstance(result, str)
    self.assertEqual(result, 'abc')

  def test_send_email_uses_given_address(self):
    """Emails are sent to the expected address."""
    emailer = MagicMock()
    adduser = AddUser(None, None, emailer)

    adduser._send_email('x@y.z', None, None, None)

    self.assertEqual(emailer.queue_email.call_count, 1)
    args, kwargs = emailer.queue_email.call_args
    self.assertEqual(args[0], 'x@y.z')

  def test_send_email_interpolates_arguments(self):
    """Emails are sent with the given arguments."""
    emailer = MagicMock()
    adduser = AddUser(None, None, emailer)

    adduser._send_email(None, 'x-first-x', 'x-user-x', 'x-pass-x')

    self.assertEqual(emailer.queue_email.call_count, 1)
    args, kwargs = emailer.queue_email.call_args
    self.assertIn('x-first-x', args[2])
    self.assertIn('x-user-x', args[2])
    self.assertIn('x-pass-x', args[2])

  def test_send_email_calls_emailer(self):
    """Emails are sent by calling emailer directly."""
    emailer = MagicMock()
    adduser = AddUser(None, None, emailer)

    adduser._send_email(None, None, None, None)

    self.assertEqual(emailer.call_emailer.call_count, 1)

  def test_adduser_fails_without_sudo(self):
    """Fail when not running as super user."""
    os = MagicMock()
    os.getuid.return_value = 1234
    adduser = AddUser(os, None, None)

    with self.assertRaises(AccountCreationException):
      adduser.adduser(None, None, None)

  def test_adduser_fails_if_user_exists(self):
    """Fail when user already exists."""
    os = MagicMock()
    os.getuid.return_value = 0
    subprocess = MagicMock()
    subprocess.check_output.return_value = b'1\n'
    adduser = AddUser(os, subprocess, None)

    with self.assertRaises(AccountCreationException):
      adduser.adduser(None, None, None)

  def test_adduser_creates_new_account_and_emails_user(self):
    """Create a new account and email the user."""
    os = MagicMock()
    os.getuid.return_value = 0
    subprocess = MagicMock()
    subprocess.check_output.return_value = b'0\n'
    emailer = MagicMock()
    adduser = AddUser(os, subprocess, emailer)

    adduser.adduser('username', 'firstname', 'email')

    self.assertTrue(os.getuid.call_count >= 1)
    self.assertTrue(subprocess.check_output.call_count >= 1)
    self.assertEqual(emailer.queue_email.call_count, 1)
    self.assertEqual(emailer.call_emailer.call_count, 1)
