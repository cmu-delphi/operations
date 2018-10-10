"""
===============
=== Purpose ===
===============

Creates new user accounts on the delphi server.

Basic sanity checks are performed, the user's home directory is setup, and an
email containing a temporary password is sent to the user.

Note that this must be run as the super user and therefore must be invoked
manually.
"""

# standard library
import argparse
import os
import random
import re
import subprocess

# first party
from delphi.operations import emailer


class AccountCreationException(Exception):
  """An Exception indicating that account creation failed."""


class AddUser:
  """Creates new user accounts on the delphi server."""

  EMAIL_SUBJECT = 'Your Delphi Account'
  EMAIL_BODY = """Hello, %s!

  An account has been created for you on host delphi.midas.cs.cmu.edu!

  You can connect via ssh using the following credentials:

  Username: %s

  Password: %s

  Please change your password ASAP. See README.md in your home directory for
  more information.

  Happy forecasting!
  """

  @staticmethod
  def new_instance():
    """Return a new instance using sensible, production-ready defaults."""
    return AddUser(os, subprocess, emailer)

  def __init__(self, os, subprocess, emailer):
    self.os = os
    self.subprocess = subprocess
    self.emailer = emailer

  def _shell_command(self, command, *args):
    """Run the given command and return the output as a string."""
    output = self.subprocess.check_output(command % args, shell=True)
    return str(output, 'utf-8')

  def _send_email(self, email, firstname, username, password):
    """
    Send an email to the given user, filling the template with the given
    values.
    """

    # generate the email using the given values
    body = AddUser.EMAIL_BODY % (firstname, username, password)
    self.emailer.queue_email(email, AddUser.EMAIL_SUBJECT, body)

    # send the email now instead of waiting for the next scheduled email update
    # (which is once per hour as of this comment)
    self.emailer.call_emailer()

  def adduser(self, username, firstname, email):
    """Add a new user account and email the password to the new user."""

    # enforce running as the super user
    if self.os.getuid() != 0:
      raise AccountCreationException('must run as super user')
    print('✔ running as super user')

    # make sure the user doesn't already exist
    cmd = 'ls -l /home | grep "%s" | wc -l'
    num_existing = int(self._shell_command(cmd, username))
    if num_existing != 0:
      raise AccountCreationException('username already exists')
    print('✔ account does not already exist')

    # create the account
    self._shell_command('adduser "%s"', username)
    print('✔ created home dir')

    # set httpd-friendly permissions on the home directory
    self._shell_command('chmod 711 /home/%s', username)
    print('✔ updated permissions')

    # assign a temporary password
    password = '%012x' % random.randrange(1 << 48)
    tempfile = self._shell_command('mktemp').strip()
    cmd = 'echo "%s" > %s && passwd --stdin "%s" < %s && rm %s'
    self._shell_command(cmd, password, tempfile, username, tempfile, tempfile)
    print('✔ assigned password')

    # email credentials to the new user
    self._send_email(email, firstname, username, password)
    print('✔ queued email for %s' % email)


def get_argument_parser():
  """Define command line arguments and usage."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'username',
      type=str,
      help='a username for the new user')
  parser.add_argument(
      'firstname',
      type=str,
      help='the new user\'s first name')
  parser.add_argument(
      'email',
      type=str,
      help='the new user\'s email address')
  return parser


def validate_args(args):
  """Validate and return command line arguments."""
  if not re.match('^\w(\w|\d){2}(\w|\d)*$', args.username):
    raise AccountCreationException('invalid username')
  if '@' not in args.email:
    raise AccountCreationException('invalid email')
  return args.username, args.firstname, args.email


def main(username, firstname, email):
  """Run this script from the command line."""
  AddUser.new_instance().adduser(username, firstname, email)


if __name__ == '__main__':
  main(*validate_args(get_argument_parser().parse_args()))
