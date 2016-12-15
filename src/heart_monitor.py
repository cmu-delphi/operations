import argparse
import time
import mysql.connector
from emailer import _send_email
import secrets


def check_heartbeat(name, timeout):
  # connect to the database
  try:
    u, p = secrets.db.auto
    cnx = mysql.connector.connect(user=u, password=p, database='automation')
  except:
    print('warning: unable to connect to the database!')
    return
  cur = cnx.cursor()

  # check the heartbeat
  cur.execute("SELECT unix_timestamp(now()) - unix_timestamp(date) FROM heartbeats WHERE name = %s", (name,))
  delta = None
  for (delta,) in cur:
    pass

  exit = False
  # handle the heartbeat
  if delta is None:
    # couldn't read it
    print('failed to check heartbeat')
  else:
    if delta < timeout:
      # good to go
      cur.execute("UPDATE heartbeats SET date = now() WHERE name = 'heart_monitor.py'")
    else:
      # blow it up
      email_from = secrets.flucontest.email_epicast
      email_to = secrets.flucontest.email_maintainer
      email_subject = 'Heart Monitor'
      email_body = 'Timeout exceeded for %s: %d >= %d' % (name, delta, timeout)
      _send_email(email_from, email_to, email_subject, email_body)
      exit = True

  # cleanup
  cur.close()
  cnx.commit()
  cnx.close()

  # blow it up
  if exit:
    raise Exception('heartbeat exceeded timeout: %d >= %d'%(delta, timeout))

if __name__ == '__main__':
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('name', type=str, help='script name (ex: automation.pl)')
  parser.add_argument('timeout', type=int, help='timeout value in seconds (ex: 900)')
  parser.add_argument('interval', type=int, help='update interval in seconds (ex: 60)')
  args = parser.parse_args()

  name = args.name #'automation.pl'
  timeout = args.timeout #900
  interval = args.interval #60

  print('Checking %s within %d seconds, every %d seconds'%(name, timeout, interval))
  while True:
    check_heartbeat(name, timeout)
    time.sleep(interval)
