#
#  ChangeSettings.py
# 
#
#  Copyright Andrew Hunter, 2007
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
# TODO: Find a way to read files multiple times.

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
    self.open_file = open(self.file, 'r+')
    self.open_file_read = open(self.file, 'r')
    self.current_open_file = self.open_file_read.read()
    self.line_check = self.regex.search(self.current_open_file)
    

  def ch_setting(self):
    """
    Adds or updates the replacement string
    """
    self.exists_check = self.regex.search(self.current_open_file)
    if self.exists_check:
      self._update()
    else:
      self._append()

  def _update(self):
    self.newlines = []
    for item in self.open_file:
      if self.line_check:
        self.newlines.append(find_memlock.sub(self.line_replacement, item))
      else:
        self.newlines.append(item)
    self._seek_write(self.newlines)

  def _seek_write(self, open_list):
    self.open_file.seek(0)
    self.open_file.writelines(open_list)
    self.open_file.truncate()
    self.open_file.flush()

  def _append(self):
    self.append_list = self.open_file.readlines()
    self.append_list[-1] = self.line_replacement + '\n\n#End of file' #Assumes that #End of file is the last line
    self._seek_write(self.append_list)

  def rm_setting(self):
    if self.line_check:
      self.remove_string = self.line_check.group() + '\n'
      print self.remove_string
      self.rm_list = self.open_file.readlines()
      self.rm_list.remove(self.remove_string)
      self._seek_write(self.rm_list)
    else:
      print "No string to remove"
