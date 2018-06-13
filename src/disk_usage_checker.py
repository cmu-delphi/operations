"""
===============
=== Purpose ===
===============

Checks disk usage and raises an Exception if any disks (really, partitions) are
nearly full.

This is useful as a canary in automation to detect low storage before it can
cause breakages.
"""

# standard library
import argparse
import subprocess


class InvalidArgsException(Exception):
  """An Exception indicating that command-line args are invalid."""


class DiskUsageException(Exception):
  """An Exception indicating that disk usage is at or above the given limit."""


class DfCommand:
  """An interface for the unix command `df`."""

  def run(self):
    """Return the output of `df -h` as a string."""
    return subprocess.check_output('df -h', shell=True).decode('utf-8')


class DiskUsageChecker:
  """Checks usage of all partitions."""

  @staticmethod
  def new_instance():
    """Return a production-ready instance."""
    return DiskUsageChecker(DfCommand())

  def __init__(self, df_command):
    """Creates a new DiskUsageChecker with the given DfCommand."""
    self.df_command = df_command

  def check_all(self, limit):
    """
    Return a tuple of disk usage diagnostics and a boolean indicating whether
    all partitions are using less than the given limit.
    """
    text = self.df_command.run()
    nominal = True
    for line in text.strip().split('\n')[1:]:
      name, size, used, avail, pct, mount = line.split()
      value = int(pct.replace('%', ''))
      if value >= limit:
        nominal = False
        break
    return text, nominal

  def raise_if_exceeds(self, limit):
    """
    Run the disk usage checker and raise an Exception if any partitions are
    used above the given limit.
    """
    text, nominal = self.check_all(limit)
    print(text, end='')
    if nominal:
      print('disk usage is nominal')
    else:
      print('disk usage exceeds %d%% (`df` to diagnose)' % limit)
      raise DiskUsageException()


def get_argument_parser():
  """Define command line arguments and usage."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'limit',
      type=int,
      help='the maximum used percent for any partition (e.g. 95)')
  return parser


def validate_args(args):
  """Validate and return command line arguments."""
  if not (0 <= args.limit <= 100):
    raise InvalidArgsException('`limit` must be in [0, 100]')
  return (args.limit,)


def main(limit):
  """Run this script from the command line."""
  DiskUsageChecker.new_instance().raise_if_exceeds(limit)


if __name__ == '__main__':
  main(*validate_args(get_argument_parser().parse_args()))
