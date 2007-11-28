#
#  memlock.py
# 
#
#  Created by Andrew Hunter on 25/11/07.
#
# TODO: Backup conf file before overwriting :P
# TODO: Come up with better varriable names
# TODO: Find a way to read files multiple times.

import re

find_memlock = re.compile('@audio - memlock \d*')
limits_conf = open('/etc/security/limits.conf', 'r+')
limits_conf_read = open('/etc/security/limits.conf', 'r')
oldlines = limits_conf_read.read()

def ch_memlock(new_memlock):
  """
  Adds or updates the @audio - memlock option in /etc/security/limits.conf
  """
  line_replacement = '@audio - memlock ' + new_memlock
  memlock_check = find_memlock.search(oldlines) #determine if an audio memlock already exists
  if memlock_check:
    print 'memlock_check is true'
    _update(line_replacement)
  else:
    _append(line_replacement)

def _update(line_replacement):
  newlines = []
  for item in limits_conf:
    line_memlock = find_memlock.search(item) #Is the current line the one we want?
    if line_memlock:
      newlines.append(find_memlock.sub(line_replacement, item))
    else:
      newlines.append(item)
  _seek_write(newlines)

def _seek_write(open_list):
  limits_conf.seek(0)
  limits_conf.writelines(open_list)
  limits_conf.truncate()
  limits_conf.flush()

def _append(line_replacement):
  append_list = limits_conf.readlines()
  append_list[-1] = line_replacement + '\n\n#End of file' #Assumes that #End of file is the last line
  _seek_write(append_list)

def rm_memlock():
  memlock_check = find_memlock.search(oldlines) #determine if an audio memlock already exists
  if memlock_check:
    memlock_string = '\n' + memlock_check.group() + '\n'
    rm_list = limits_conf.readlines()
    rm_list.remove(memlock_string)
    _seek_write(rm_list)
  else:
    print "No memlock to remove"
  

