#!/usr/bin/python3

from rtinfo import RTInfo

rtinfo = RTInfo()
user_list = rtinfo.user_list()
rlimits = rtinfo.rlimits()

print("-- username, full name, audio group:")
print(user_list)
print("-- user session has rtprio and memlock at supported levels?:")
print(rlimits)