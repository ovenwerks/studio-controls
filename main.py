#!/usr/bin/env python

import gtk
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
      "on_mainWindow_destroy" : gtk.main_quit }
    self.wTree.signal_autoconnect(dic)

  def closeButton_clicked(self, widget):
	gtk.main_quit()

print __name__
if __name__ == "__main__":
  uscontrols = Uscontrols()
  gtk.main()
