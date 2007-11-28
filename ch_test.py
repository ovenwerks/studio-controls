#!/usr/bin/python

import changesettings

memlock = changesettings.ChangeSettings('/etc/security/limits.conf', '@audio - memlock (\d*)', '@audio - memlock 512000')

memlock.ch_setting()
