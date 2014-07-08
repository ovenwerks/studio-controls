#!/usr/bin/python3

import os
import re

class AudioConfig:

    def audio_config_check()
        '''Make ure /etc/security/limits.d/audio.conf exists and that there aren't conflicting settings in other files under /etc/security/.'''
        # make sure /etc/security/limits.d/audio.conf does not diff from supplied audio.conf
        # make sure /etc/security/limits.d/audio.conf.disabled does not exist
        # make sure there are no lines with @audio in any other file in /etc/security/, if so, report it
        # see if /etc/udev/rules.d/60-raw1394.rules exists
        pass

    def rm_1394_rule()
        '''Remove obsolete udev file that was used to gain privilege for raw1394 devices'''
        pass

    def audio_conf_setup()
        '''Set up /etc/security/limits.d/audio.conf'''
        # copy supplied file to the right path
        pass