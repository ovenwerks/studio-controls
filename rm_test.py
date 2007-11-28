#!/usr/bin/python

#Example for removing the memlock line from limits.conf

import changesettings

memlock = changesettings.ChangeSettings('/etc/security/limits.conf', '@audio - memlock (\d*)', '@audio - memlock')

memlock.rm_setting()
