#!/usr/bin/python
#
#  Copyright Andrew Hunter, Luis de Bethencourt Guimera 2007
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

import gtk, changesettings
from gtk import glade

class Uscontrols:
  def __init__(self):
    #Set the Glade file
    self.gladefile = "gui.glade"
    self.wTree = gtk.glade.XML(self.gladefile)

    #Get the Main Window, and connect the "destroy" event
    self.window = self.wTree.get_widget("mainWindow")

    #Create our dictionay and connect it
    dic = { "on_closeButton_clicked" : self.closeButton_clicked,
      "on_mainWindow_destroy" : gtk.main_quit,
      "on_apply_button_clicked" : self.apply_settings,
      "on_memlock_spinbutton_value_changed" : self.update_memlock_amount,
      "on_memlock_checkButton_toggled" : self.set_memlock_enable}
    self.wTree.signal_autoconnect(dic)

  #For each setting to change, create an instance
  memlock = changesettings.ChangeSettings("/etc/security/limits.conf", "@audio - memlock (\d*)", "")

  def closeButton_clicked(self, widget):
    gtk.main_quit()

  def apply_settings(self, apply_button):
    print self.memlock.line_replacement
    if self.set_memlock_enable.memlock_enabled:
      self.memlock.ch_setting()
    elif self.set_memlock_enable.memlock_enabled == False:
      self.memlock.rm_setting()

  def update_memlock_amount(self, spin_object):   
    #Check to make sure that the value entered is an interger, then convert it to a string
    memlock_entry_amount = str(spin_object.get_value_as_int())
    self.memlock.line_replacement = "@audio - memlock " + memlock_entry_amount + "000"
    print self.memlock.line_replacement

  def set_memlock_enable(self, memlock_checkButton): #FIXME: Use dispatcher funtion instead
    memlock_enabled = memlock_checkButton.get_active()
    widget = self.wTree.get_widget('memlock_spinbutton')
    widget.set_sensitive(memlock_checkButton.get_active())
    print memlock_enabled
    return memlock_enabled

print __name__
if __name__ == "__main__":
  uscontrols = Uscontrols()
  gtk.main()
