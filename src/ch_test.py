#!/usr/bin/python

# Example of ch_setting method

import changesettings, sys, os.path, cPickel

our_conf = os.path.expanduser('~/.ubuntustudio-controls')

memlock_string = '512000' #define memlock_string incase our file does not exist. In the gui this will be unnecessary.

try:
  global settings_file = open(our_conf, 'r+') #Try and open our file
  global memlock_string = cPickel.load(settings_file) #Only limitiation here is one setting per file. Might want to use a list for more varriables
except IOerror:
  print 'IOerror: Can not read file for some reason. Continueing with default value'

memlock = changesettings.ChangeSettings('/etc/security/limits.conf', '@audio - memlock (\d*)', '@audio - memlock' + memlock_string)

memlock.ch_setting()

cPickle.dump(memlock_string, settings_file)

settings_file.close()
