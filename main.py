#!/usr/bin/env python

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
      "on_memlock_spinbutton_value_changed" : self.update_memlock_amount}
    self.wTree.signal_autoconnect(dic)

    #For each setting to change, create an instance
    memlock = changesettings.ChangeSettings('/etc/security/limits.conf', '@audio - memlock (\d*)', '')

  def closeButton_clicked(self, widget):
    gtk.main_quit()

  def apply_settings():
    if memlock_enable:
      self.memlock.ch_setting()
    else:
      self.memlock.rm_setting()

  def update_memlock_amount(): #FIXME: Needs to take two arguments as supplied by gtk... 
    #Check to make sure that the value entered is an interger, then conver it to a string
    memlock_entry_amount = str(int(self.wTree.get_widget("memlock_spinbutton").get_value()))
    self.memlock.line_replacement = '@audio - memlock ' + memlock_entry_amount 
     
print __name__
if __name__ == "__main__":
  uscontrols = Uscontrols()
  gtk.main()
