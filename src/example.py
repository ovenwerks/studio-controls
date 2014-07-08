#!/usr/bin/python3

from getinfo import GetInfo

info = GetInfo()
user_list = info.user_list()
rlimits = info.rlimits()

print("-- username, full name, audio group:")
print(user_list)
print("-- user session has rtprio and memlock at supported levels?:")
print(rlimits)