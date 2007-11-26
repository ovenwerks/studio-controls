#
#  memlock.py
# 
#
#  Created by Andrew Hunter on 25/11/07.
#
# TODO: Add way to append the correct line if one does not exist.
# TODO: Backup conf file before overwriting :P

import re

find_memlock = re.compile('@audio - memlock (\d{6})')

def ch_memlock(new_memlock):
  line_replacement = '@audio - memlock ' + new_memlock
  limits_conf = open('/etc/security/limits.conf', 'r+')
  oldlines = limits_conf.read()
  newlines = find_memlock.sub(line_replacement, oldlines)
  limits_conf.seek(0)
  limits_conf.write(newlines)
  limits_conf.close()

