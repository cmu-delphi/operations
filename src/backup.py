"""Makes backups of Delphi files and databases."""

# standard library
import datetime
import os
import subprocess
import time

# first party
import delphi.operations.secrets as secrets


#General setup
dest = '/home/automation/backups'
tag = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
print('Destination: %s | Tag: %s'%(dest, tag))

#Directories
dirs = [
  {
    'label': 'auto',
    'path': '/home/automation',
    'name': 'driver',
    'exclude': 'flu_data',
  }, {
    'label': 'data',
    'path': '/home/automation/driver',
    'name': 'flu_data',
  },
]

# previously backed-up paths
# keys_path, keys_name = os.path.split(secrets.apache.keys_dir)
# {
#   'label': 'html',
#   'path': '/var/www',
#   'name': 'html',
# },
# {
#   'label': 'keys',
#   'path': keys_path,
#   'name': keys_name,
# },

#Databases
dbs = [
  'automation',
  'epicast2',
  'epidata',
  'utils',
]

#Utils
def get_size(file):
  return str(subprocess.check_output('du -h %s/%s'%(dest, file), shell=True), 'utf-8').split('\t')[0]

#Each directory is backed up to it's own archive (*.tgz)
#All databases are backed up at once to a single archive (*.sql.gz)
#This list of archives is used to create a final archive containing all the others
archives = []

#Backup directories
for dir in dirs:
  print(' Directory: %s/%s'%(dir['path'], dir['name']))
  if 'exclude' not in dir or dir['exclude'] is None:
    exclude = ''
  else:
    exclude = '--exclude %s'%(dir['exclude'])
  file = 'backup_%s_%s.tgz'%(tag, dir['label'])
  subprocess.check_call('tar -czf %s/%s -C %s %s %s'%(dest, file, dir['path'], exclude, dir['name']), shell=True)
  print(' %s'%(get_size(file)))
  archives.append(file)

#Backup databases
list = ' '.join(dbs)
print(' Databases: %s'%(list))
file = 'backup_%s_database.sql'%(tag)
u, p = secrets.db.backup
# TODO Revert when big tables are gone
#subprocess.check_call('mysqldump --user=%s --password=%s --databases %s > %s/%s'%(u, p, list, dest, file), shell=True)
subprocess.check_call('mysqldump --user=%s --password=%s --databases %s --ignore-table=epidata.covidcast_legacy --ignore-table=epidata.covidcast_backup --ignore-table=epidata.covidcast > %s/%s'%(u, p, list, dest, file), shell=True)
subprocess.check_call('gzip %s/%s'%(dest, file), shell=True)
file += '.gz'
print(' %s'%(get_size(file)))
archives.append(file)

#Create the final archive
print(' Building final archive')
file = 'backup_%s.tar'%(tag)
final_archive = '%s/%s'%(dest, file)
subprocess.check_call('tar -cf %s -C %s %s'%(final_archive, dest, ' '.join(archives)), shell=True)
print(' %s'%(get_size(file)))

#Delete the intermediate archives
for file in archives:
  os.remove('%s/%s'%(dest, file))

# TODO: Send the backup to an external drive
# subprocess.check_call('cp -v %s /mnt/usb2t/backups/'%(final_archive), shell=True)

# TODO: Send the backup offsite

#Success
print('Backup completed successfully!')
