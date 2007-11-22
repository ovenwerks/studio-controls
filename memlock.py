#
#  memlock.py
# 
#
#  Created by Andrew Hunter on 25/11/07.
#
# TODO: Add way to append the correct line if one does not exist.

import re

find_memlock = re.compile('@audio - memlock (\d{6})') #create the regex that we are looking for

line_replacement = '@audio - memlock ' #FIXME: Make the user input varriables

new_memlock = '512000'

limits_conf = '/etc/security/limits.conf'

def ch_memlock(line_replacement, new_memlock, limits_conf):
  for line in fileinput.FileInput(limit_conf, inplace=1):
    try:
        find_memlock.sub(line_replacement + new_memlock, line)
    except:
        print 'There has been a error with the string substution.'


   
