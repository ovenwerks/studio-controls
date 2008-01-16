#
#  ChangeSettings.py
# 
#
#  Copyright Andrew Hunter, 2008
#
#   This program is free software; you may redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the Free 
#   Software Foundation; either version 2 of the License, or (at your option) 
#   any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
#   FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
#   more details.
#
# TODO: Backup conf file before overwriting :P
# TODO: Come up with better varriable names

import re

class ChangeSettings:
  """
  ChangeSettings requires three strings as arguments:
  1) The file to operate on
  2) The python regular expression to look for
  3) The string to replace
  """

  def __init__(self, file_input, regex_string, line_replacement):
    self.file = file_input
    self.regex_string = regex_string
    self.line_replacement = line_replacement
    self.regex = re.compile(self.regex_string)

  def regex_search(self):
    self.open_file_read = open(self.file, 'r')
    self.current_open_file = self.open_file_read.read()
    self.line_check = self.regex.search(self.current_open_file)
    return self.line_check

  def _open_file(self):
    self.open_file = open(self.file, 'r+')
    return self.open_file

  def _append(self):
    self.open_file = self._open_file()
    self.append_list = self.open_file.readlines()
    self.to_add = self.line_replacement + '\n'
    self.append_list.insert(-1, self.to_add)
    self._seek_write(self.append_list)

  def _update(self):
    self.newlines = [self.regex.sub(self.line_replacement, item) for item in self._open_file()]
    self._seek_write(self.newlines)

  def _seek_write(self, open_list):
    self.open_file.seek(0)
    self.open_file.writelines(open_list)
    self.open_file.truncate()
    self.open_file.flush()

  def ch_setting(self):
    """
    Adds or updates the replacement string
    """
    self.line_check = self.regex_search()
    if self.line_check:
      self._update()
    else:
      self._append()

  def rm_setting(self):
    self.open_file = self._open_file()
    self.line_check = self.regex_search()
    if self.line_check:
      self.remove_string = self.line_check.group() + '\n'
      print self.remove_string
      self.rm_list = self.open_file.readlines()
      self.rm_list.remove(self.remove_string)
      self._seek_write(self.rm_list)
    else:
      print "No matches in file"

