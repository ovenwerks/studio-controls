#!/usr/bin/python3

import os
import re
import filecmp

class AudioConfig:

    def __init__(self):

        self.audio_conf_file = "/etc/security/limits.d/audio.conf"
        self.audio_conf_file_disabled = self.audio_conf_file + ".disabled"
        self.audio_conf_file_us_supplied = "/usr/share/ubuntustudio-controls/audio.conf"

        self.audio_conf_replace = False
        self.audio_conf_disabled_remove = False
        self.audio_conf_cleanup = False
        # self.raw1394_rule_rm = False

    def audio_config_check(self):
        '''Make sure /etc/security/limits.d/audio.conf exists and that there aren't 
            conflicting settings in other files under /etc/security/.'''

        if os.path.isfile(self.audio_conf_file): # see if file exists
            if filecmp.cmp(self.audio_conf_file, self.audio_conf_file_us_supplied): #compare files
                self.audio_conf_replace = False
            else:
                self.audio_conf_replace = True
        else:
            self.audio_conf_replace = True

        if os.path.isfile(self.audio_conf_file_disabled): # see if file exists
            self.audio_conf_disabled_remove = True

        # make sure there are no lines with @audio in any other file in /etc/security/, if so, report it
        # if ..
            # self.audio_conf_cleanup = True

        audio_configs = { 'audio_conf_replace' : self.audio_conf_replace,
                          'audio_conf_disabled_remove' : self.audio_conf_disabled_remove,
                          'audio_conf_cleanup' : self.audio_conf_cleanup }
        return audio_configs

    def audio_config_setup(self, conf_replace, conf_disabled_remove, conf_cleanup):

        r = [conf_replace, conf_disabled_remove, conf_cleanup]
        return r
