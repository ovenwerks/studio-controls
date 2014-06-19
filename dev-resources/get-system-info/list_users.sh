#!/bin/bash

# found on internet - could be redone in python

# Name: listusers.bash
# Purpose: List all normal user accounts in the system. Tested on RHEL / Debian Linux
# Author: Vivek Gite <www.cyberciti.biz>, under GPL v2.0+
# -----------------------------------------------------------------------------------

_LOGIN_DEFS="/etc/login.defs"
_PASSWD_FILE="/etc/passwd"

## get min UID limit
_MIN=$(grep "^UID_MIN" $_LOGIN_DEFS)

## get max UID limit
_MAX=$(grep "^UID_MAX" $_LOGIN_DEFS)

## use awk to print if UID >= $MIN and UID <= $MAX and shell is not /sbin/nologin
awk -F':' -v "min=${_MIN##UID_MIN}" -v "max=${_MAX##UID_MAX}" '{ if ( $3 >= min && $3 <= max  && $7 != "/usr/sbin/nologin" ) print $1 }' "$_PASSWD_FILE"
