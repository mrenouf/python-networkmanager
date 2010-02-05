#!/usr/bin/python

import glib
import gtk
import dbus

ETH="802-3-ethernet"

NM_NAME="org.freedesktop.NetworkManager"
NM_PATH="/org/freedesktop/NetworkManager"
NM_IFACE="org.freedesktop.NetworkManager"
NM_SETTINGS_PATH="/org/freedesktop/NetworkManagerSettings"
NM_SETTINGS_IFACE="org.freedesktop.NetworkManagerSettings"

class NetworkManager(object):
	def __init__(self, bus):
		self.bus = bus
		self.proxy = self.bus.get_object(NM_NAME, NM_PATH)
		self.settings = bus.get_object(NM_NAME, NM_SETTINGS_PATH)

	def __getattr__(self, name):
		return self.proxy.Get(NM_IFACE, name)
	
	def get_devices(self):
		"""
		Returns a list of object paths of network devices known to the system
		"""
		#		for d in self.proxy.GetDevices():	
		return [NetworkManagerDevice(self.bus, d) for d in self.proxy.GetDevices()];

	def activate_connection(self):
		pass
	
	def deactivate_connection(self):
		pass
		
	def sleep(self, sleep):
		pass
	
	def list_connections(self):
		return self.settings.ListConnections(dbus_interface=NM_SETTINGS_IFACE)
		
	def add_connection(self):
		pass
		
	def get_connection(self, path):
		return NetworkManagerConnection(self.bus, path)
		
		
	def get_settings(self):
		"""
		Returns a wrapper providing access to NetorkManagerSettings 
		for accessing system connection settings
		"""
		return self.settings


class NetworkManagerDevice(object):
	#self.interface = 

	def __init__(self, bus, object_path):
		self.proxy = bus.get_object("org.freedesktop.NetworkManager", object_path)
		self.type = self.proxy.Get('org.freedesktop.NetworkManager.Devices', 'DeviceType')
	
	def __getattr__(self, name):
		return self.proxy.Get('org.freedesktop.NetworkManager.Devices', name)
				
	def __setatrtr__(self, name, value):
		print name
		self.props.Set('org.freedesktop.NetworkManager.Devices', name, value)
		
	#return self.proxy.get_dbus_method("Foo", dbus_interface='com.example.Bar')(123)

	def device_type(self):
		return ["Unknown", "Ethernet", "Wifi", "GSM", "CDMA"][self.type]
	
	def is_managed(self):
		pass
	
	def disconnect(self):
		self.device.Disconnect()

class NetworkManagerSettings():
	def __init__(self, bus):
		self.proxy = bus.get_object(NM_NAME, NM_SETTINGS_PATH)
		
	def list_connections(self):
		return self.proxy.ListConnections(dbus_interface=NM_SETTINGS_IFACE)
	
	def add_connection(self, properties):
		pass
	
class NetworkManagerConnection():
	def __init__(self, bus, connection):
		self.proxy = bus.get_object("org.freedesktop.NetworkManager", connection);
	
	def get_settings(self):
		"""
		Returns this connections settings - a{sa{sv}} (String_String_Variant_Map_Map)
		The nested settings maps describing this object.
		"""
		return self.proxy.GetSettings(dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')
		
	def delete(self):
		self.proxy.Delete(dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')

	def update(self, properties):
		self.proxy.Update(properties, dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')


class NetworkManagerDeviceWired(NetworkManagerDevice):
	def __init__(self, bus, object_path):
		super(NetworkManagerDeviceWired, self).__init__(bus, object_path)


if __name__ == "__main__":
	bus = dbus.SystemBus()
	nm = NetworkManager(bus)
	print nm.WirelessEnabled
	print nm.WirelessHardwareEnabled
	print nm.ActiveConnections
	print nm.State
	
	for device in nm.get_devices():
		print device.Udi
		print device.device_type()
		
	set = NetworkManagerSettings(bus)
	print set.list_connections()[0]
	
	print "=========="
	con = NetworkManagerConnection(bus, set.list_connections()[0])

	set = con.get_settings()
	print "Type: %s" % set['connection']['type']
	print "UUID: %s" % set['connection']['uuid']
	print "Connection %s: " % set['connection']['id']
	print "Routes: %s" % set['ipv4']['routes']
	print "Addresses: %s" % set['ipv4']['addresses']
	print "DNS: %s" % set['ipv4']['dns']
	print "Method: %s" % set['ipv4']['method']
	
	#print set
	#['802-3-ethernet']['mac-address']
	#for k in con.get_settings().keys():
	#	for v in k.keys():
	#		print v

