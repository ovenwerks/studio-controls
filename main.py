#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class Uscontrols:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("Ubuntu Studio Controls")
	
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)

		self.window.set_border_width(10)

		self.windowIcon = self.window.render_icon(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_BUTTON)
		self.window.set_icon(self.windowIcon)

		# First row
		self.hbox1 = gtk.HBox(False, 10)

		# Memlock Radio Button
		self.memlock_radio = gtk.CheckButton(None, False)
		self.memlock_radio.set_active(False)
		self.memlock_radio.connect_object("clicked", self.memlock_radio_clck, None)
		self.hbox1.pack_start(self.memlock_radio, True, True, 0)

		# Memlock Label "Enable memlock"
		self.memlock_labelEm = gtk.Label("Enable memlock")
		self.hbox1.pack_start(self.memlock_labelEm, True, True, 0)

		# Memlock Text Entry
		self.memlock_textEntry = gtk.Entry()
		self.hbox1.pack_start(self.memlock_textEntry, True, True, 0)

		# Memlock Label "mb"
		self.memlock_labelMb = gtk.Label("MB")
		self.hbox1.pack_start(self.memlock_labelMb, True, True, 0)

		# Second row
		self.hbox2 = gtk.HBox(False, 0)

		# Credits
		self.credits = gtk.Button("Credits", gtk.STOCK_ABOUT)
		self.credits.connect_object("clicked", self.hello, None)
		self.hbox2.pack_start(self.credits, True, True, 0)

		# Apply
		self.apply = gtk.Button("Apply", gtk.STOCK_APPLY)
		self.apply.connect_object("clicked", self.hello, None)
		self.hbox2.pack_start(self.apply, True, True, 0)

		# OK
		self.close = gtk.Button("Close", gtk.STOCK_CLOSE)
		self.close.connect_object("clicked", self.destroy, None)
		self.hbox2.pack_start(self.close, True, True, 0)

		# Vertical placing
		self.hseparator = gtk.HSeparator()
		self.vbox1 = gtk.VBox(False, 20)
		self.window.add(self.vbox1)
		self.vbox1.pack_start(self.hbox1, True, True, 0)
		self.vbox1.pack_start(self.hseparator, True, True, 0)
		self.vbox1.pack_start(self.hbox2, True, True, 0)


		# Show all
		self.memlock_radio.show()
		self.memlock_labelEm.show()
		self.memlock_textEntry.show()
		self.memlock_labelMb.show()
		self.hbox1.show()
		self.credits.show()
		self.apply.show()
		self.close.show()
		self.hbox2.show()
		self.vbox1.show()
		self.window.show()

	def hello(self, widget, data=None):
		print "Hello World"

	def memlock_radio_clck(self, widget, data=None):
		print "memlock_radio_clck"

	def delete_event(self, widget, event, data=None):
		print "delete event occurred"
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def main(self):
		gtk.main()

print __name__
if __name__ == "__main__":
	uscontrols = Uscontrols()
	uscontrols.main()
