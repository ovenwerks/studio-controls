#!/usr/bin/python3

import resource
import re
import os
import filecmp

class GetInfo:
    """Functions for getting info about rt privilege in the system"""


    def __init__(self):

        self.audio_conf_file = "/etc/security/limits.d/audio.conf"
        self.audio_conf_file_disabled = self.audio_conf_file + ".disabled"
        self.audio_conf_file_us_supplied = "/usr/share/ubuntustudio-controls/audio.conf"


    def user_list(self):
        """Lists "real" users and shows whether they are in audio group, or not"""


        real_users = [] #users that are within UID limits and have a login shell
        users = [] #this will be the actual list of users in the format: user_name full_name in_audio_group(True/False)
        login_defs = open("/etc/login.defs", "r")
        passwd_file = open("/etc/passwd", "r")
        groups_file = open("/etc/group", "r")


        # get min and max UID values
        for line in login_defs:
            if re.match("^UID_MIN", line):
                uid_min_expr = re.compile('\d+')
                uid_min=int(uid_min_expr.findall(line)[0])
            if re.match("^UID_MAX", line):
                uid_max_expr = re.compile('\d+')
                uid_max=int(uid_max_expr.findall(line)[0])


        # create a list of real users based on UID limits and login shell
        for line in passwd_file:
            l = line.rstrip().split(':')
            uid = int(l[2])
            if uid >= uid_min and uid <= uid_max and l[6] != '/usr/sbin/nologin':
                real_users.append(l)


        # create a list of users who are members of audio group
        for line in groups_file:
            if re.match("^audio", line):
                audio_users = line.split(':')[3].rstrip().split(',')


        # create the list of users and their attributes that we are interested in
        for user in real_users:
            user_name = user[0]
            full_name = user[4].strip(",,,")
            if user_name in audio_users:
                users.append([user_name, full_name, True])
            else:
                users.append([user_name, full_name, False])


        return users


    def rlimits(self):
        """Simply checks if the current user session has acceptable hard limits for rtprio and memlock.
        Currently, supported values are exactly how the audio.conf file from jackd package sets them."""
        if resource.getrlimit(resource.RLIMIT_RTPRIO)[1] == 95 or resource.getrlimit(resource.RLIMIT_MEMLOCK)[1] == -1:
            return True
        else:
            return False

    def audio_config_check(self):
        '''Checks whether /etc/security/limits.d/audio.conf exists and has appropriate levels'''

        if os.path.isfile(self.audio_conf_file): # see if file exists
            if filecmp.cmp(self.audio_conf_file, self.audio_conf_file_us_supplied): #compare files
                return True
            else:
                return False