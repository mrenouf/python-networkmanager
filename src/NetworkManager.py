#!/usr/bin/python

import glib
import gtk
import dbus

class NetworkManager(object):

	def __init__(self):
		self.bus = dbus.SystemBus()
		self.proxy = self.bus.get_object(
			"org.freedesktop.NetworkManager",
			"/org/freedesktop/NetworkManager")
			
		#self.GetDevices = self.proxy.get_dbus_method("GetDevices", dbus_interface='com.example.Bar')

	def __getattr__(self, name):
		return self.proxy.Get('org.freedesktop.NetworkManager', name)
	
	def get_devices(self):
		"""
		Returns a list of object paths of network devices known to the system
		"""
		return [NetworkManagerDevice(self.bus, d) for d in self.proxy.GetDevices()];

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

class NetworkManagerDeviceWired(NetworkManagerDevice):
	def __init__(self, bus, object_path):
		super(NetworkManagerDeviceWired, self).__init__(bus, object_path)


if __name__ == "__main__":
	nm = NetworkManager()
	print nm.WirelessEnabled
	print nm.WirelessHardwareEnabled
	print nm.ActiveConnections
	print nm.State
	
	for device in nm.get_devices():
		print device.Udi
		print device.device_type()

	

