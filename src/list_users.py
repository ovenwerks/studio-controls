#!/usr/bin/python3

import sys
import re


# Get list of real users
def get_real_users():

    real_users = []

    login_defs = open("/etc/login.defs", "r")
    passwd_file = open("/etc/passwd", "r")

    # get min and max UID values
    for line in login_defs:
        if re.match("^UID_MIN", line):
            uid_min_expr = re.compile('\d+')
            uid_min=int(uid_min_expr.findall(line)[0])
        if re.match("^UID_MAX", line):
            uid_max_expr = re.compile('\d+')        
            uid_max=int(uid_max_expr.findall(line)[0])

    # only list users that have UID within limits and has a login shell
    for line in passwd_file:
        l = line.split(':')
        uid = int(l[2])
        if uid >= uid_min and uid <= uid_max and l[6] != '/usr/sbin/nologin':
            real_users.append(l)

    return real_users

users = get_real_users()
print(users)
