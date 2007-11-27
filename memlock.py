#
#  memlock.py
# 
#
#  Created by Andrew Hunter on 25/11/07.
#
# TODO: Add way to append the correct line if one does not exist.
# TODO: Backup conf file before overwriting :P
# TODO: Come up with better varriable names

import re

find_memlock = re.compile('@audio - memlock \d*')
limits_conf = open('/etc/security/limits.conf', 'r+')
limits_conf_append = open('/etc/security/limits.conf', 'a+')
oldlines = limits_conf.read()

def ch_memlock(new_memlock):
  line_replacement = '@audio - memlock ' + new_memlock
  memlock_check = find_memlock.search(oldlines) #determine if an audio memlock already exists
  if memlock_check:
    _update(line_replacement)
    limits_conf.close()
  else:
    limits_conf.close()
    _append(line_replacement)
    limits_conf_append.close()

def _update(line_replacement):
  newlines = find_memlock.sub(line_replacement, oldlines)
  limits_conf.seek(0)
  limits_conf.write(newlines)

def _append(line_replacement): #FIXME: Does not respect #End of file.
  limits_conf_append.seek(-14, 2)
  limits_conf_append.write('\n' + line_replacement + '\n')

