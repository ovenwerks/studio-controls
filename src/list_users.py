#!/usr/bin/python3

import re

def list_users():

    real_users = []

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

    # create a list with the format: <user_name>, <full_name>, <audio_group_bool>
    users = []
    for user in real_users:
        user_name = user[0]
        full_name = user[4].strip(",,,")

        if user_name in audio_users:
            users.append([user_name, full_name, True])
        else:
            users.append([user_name, full_name, False])

    return users


l_users = list_users()

print(l_users)
