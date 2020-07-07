#!/bin/sh
# send signal to autojack
/usr/bin/dbus-send --system --type=signal / org.studio.control.event.${1}_signal

# Note: in most cases -controls can automatoically switch from speakers
#		to phones and back via alsa controling. In some cases pin
#		function needs to be changed as root. This would be the place to
#		add that below.

