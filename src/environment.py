"""A helper class that provides information about the runtime environment."""

# standard library
import socket


class Environment:

  @staticmethod
  def is_prod():
    """Return whether this is running in production."""
    return socket.gethostname() == 'delphi-master-prod-01.delphi.cmu.edu'
