#!/usr/bin/python

import glib
import gtk
import dbus

class DbusTest(object):
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("dbus_test.xml")
        builder.connect_signals(self)
        self.bus_name = builder.get_object("bus_name_text")
        self.object_path = builder.get_object("object_path_text")
        self.result_text = builder.get_object("result_text")
        self.statusbar = builder.get_object("statusbar")
        self.statusbar_context_id = self.statusbar.get_context_id("Error Messages")
        window = builder.get_object("main_window")
        window.show_all()

        #self.bus = dbus.SessionBus()
        self.bus = dbus.SystemBus()
    

    def main_window_delete_event_cb(self, window, event):
        gtk.main_quit()
    

    def get_object_button_clicked_cb(self, button):
        bus_name = self.bus_name.get_text()
        object_path = self.object_path.get_text()

        text = ""

        try:
            obj = self.bus.get_object(bus_name, object_path)
        except dbus.exceptions.DBusException, e:
            self.statusbar.push(self.statusbar_context_id, str(e))
        except ValueError, e:
            self.statusbar.push(self.statusbar_context_id, str(e))

	text = dir(obj)
	#str(obj)            
        buffer = self.result_text.get_buffer()
        buffer.set_text(text)

if __name__=="__main__":
    DbusTest()
    gtk.main()

#win.connect("delete-event", quit)
#win.show_all()
#dir(nm)
#print nm
