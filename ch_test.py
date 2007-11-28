#!/usr/bin/python

# Example of ch_setting method

import changesettings

memlock = changesettings.ChangeSettings('/etc/security/limits.conf', '@audio - memlock (\d*)', '@audio - memlock 512000')

memlock.ch_setting()
