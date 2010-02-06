#!/usr/bin/python

import glib
import gtk
import dbus
import enum

ETH="802-3-ethernet"

NM_NAME="org.freedesktop.NetworkManager"
NM_PATH="/org/freedesktop/NetworkManager"
NM_IFACE="org.freedesktop.NetworkManager"
NM_DEVICE_IFACE="org.freedesktop.NetworkManager.Device"
NM_DEVICE_WIRED_IFACE="org.freedesktop.NetworkManager.Device.Wired"
NM_SETTINGS_PATH="/org/freedesktop/NetworkManagerSettings"
NM_SETTINGS_IFACE="org.freedesktop.NetworkManagerSettings"

DeviceType = enum.new("DeviceType", UNKNOWN=0, ETHERNET=1, WIFI=2, GSM=3, CDMA=4)

DeviceState = enum.new("DeviceState", 
	#The device is in an unknown state.
	UNKNOWN = 0,
	#The device is not managed by NetworkManager.
	UNMANAGED = 1,
	#The device cannot be used (carrier off, rfkill, etc).
	UNAVAILABLE = 2,
	#The device is not connected.
	DISCONNECTED = 3,
	#The device is preparing to connect.
	PREPARE = 4,
	#The device is being configured.
	CONFIG = 5,
	#The device is awaiting secrets necessary to continue connection.
	NEED_AUTH = 6,
	#The IP settings of the device are being requested and configured.
	IP_CONFIG = 7,
	#The device is active.
	ACTIVATED = 8,
	#The device is in a failure state following an attempt to activate it.
	FAILED = 9
)

DeviceCap = enum.new("DeviceCap", 
	NONE = 0,
	SUPPORTED = 1,
	CARRIER_DETECT = 2,
)

DeviceStateReason = enum.new("DeviceStateReason", 
	#The reason for the device state change is unknown.
	UNKNOWN = 0,
	#The state change is normal.
	NONE = 1,
	#The device is now managed.
	NOW_MANAGED = 2,
	#The device is no longer managed.
	NOW_UNMANAGED = 3,
	#The device could not be readied for configuration.
	CONFIG_FAILED = 4,
	#IP configuration could not be reserved (no available address, timeout, etc).
	CONFIG_UNAVAILABLE = 5,
	#The IP configuration is no longer valid.
	CONFIG_EXPIRED = 6,
	#Secrets were required, but not provided.
	NO_SECRETS = 7,
	#The 802.1X supplicant disconnected from the access point or authentication server.
	SUPPLICANT_DISCONNECT = 8,
	#Configuration of the 802.1X supplicant failed.
	SUPPLICANT_CONFIG_FAILED = 9,
	#The 802.1X supplicant quit or failed unexpectedly.
	SUPPLICANT_FAILED = 10,
	#The 802.1X supplicant took too long to authenticate.
	SUPPLICANT_TIMEOUT = 11,
	#The PPP service failed to start within the allowed time.
	PPP_START_FAILED = 12,
	#The PPP service disconnected unexpectedly.
	PPP_DISCONNECT = 13,
	#The PPP service quit or failed unexpectedly.
	PPP_FAILED = 14,
	#The DHCP service failed to start within the allowed time.
	DHCP_START_FAILED = 15,
	#The DHCP service reported an unexpected error.
	DHCP_ERROR = 16,
	#The DHCP service quit or failed unexpectedly.
	DHCP_FAILED = 17,
	#The shared connection service failed to start.
	SHARED_START_FAILED = 18,
	#The shared connection service quit or failed unexpectedly.
	SHARED_FAILED = 19,
	#The AutoIP service failed to start.
	AUTOIP_START_FAILED = 20,
	#The AutoIP service reported an unexpected error.
	AUTOIP_ERROR = 21,
	#The AutoIP service quit or failed unexpectedly.
	AUTOIP_FAILED = 22,
	#Dialing failed because the line was busy.
	MODEM_BUSY = 23,
	#Dialing failed because there was no dial tone.
	MODEM_NO_DIAL_TONE = 24,
	#Dialing failed because there was carrier.
	MODEM_NO_CARRIER = 25,
	#Dialing timed out.
	MODEM_DIAL_TIMEOUT = 26,
	#Dialing failed.
	MODEM_DIAL_FAILED = 27,
	#Modem initialization failed.
	MODEM_INIT_FAILED = 28,
	#Failed to select the specified GSM APN.
	GSM_APN_FAILED = 29,
	#Not searching for networks.
	GSM_REGISTRATION_NOT_SEARCHING = 30,
	#Network registration was denied.
	GSM_REGISTRATION_DENIED = 31,
	#Network registration timed out.
	GSM_REGISTRATION_TIMEOUT = 32,
	#Failed to register with the requested GSM network.
	GSM_REGISTRATION_FAILED = 33,
	#PIN check failed.
	GSM_PIN_CHECK_FAILED = 34,
	#Necessary firmware for the device may be missing.
	FIRMWARE_MISSING = 35,
	#The device was removed.
	REMOVED = 36,
	#NetworkManager went to sleep.
	SLEEPING = 37,
	#The device's active connection was removed or disappeared.
	CONNECTION_REMOVED = 38,
	#A user or client requested the disconnection.
	USER_REQUESTED = 39,
	#The device's carrier/link changed.
	CARRIER = 40,
	#The device's existing connection was assumed.
	CONNECTION_ASSUMED = 41,
	#The 802.1x supplicant is now available.
	SUPPLICANT_AVAILABLE = 42,
)

class NetworkManagerDevice(object):
	def __init__(self, bus, object_path):
		self.proxy = bus.get_object(NM_NAME, object_path)
	
	def getattr__(self, name):
		return self.proxy.Get(NM_DEVICE_IFACE, name)

	def disconnect(self):
		self.proxy.Disconnect()

	@property
	def udi(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Udi")

	@property
	def interface(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Interface")

	@property
	def driver(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Driver")

	@property
	def capabilities(self):
		return DeviceCap.from_value(self.proxy.Get(NM_DEVICE_IFACE, "Capabilities"))

	@property
	def ipv4_address(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Ip4Address")

	@property
	def state(self):
		return DeviceState.from_value(self.proxy.Get(NM_DEVICE_IFACE, "State"))

	@property
	def ipv4config(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Ip4Config")

	@property
	def dhcp4config(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Dhcp4Config")

	@property
	def ip6config(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Ip6Config")

	@property
	def managed(self):
		return self.proxy.Get(NM_DEVICE_IFACE, "Managed")

	@property
	def type(self):
		return DeviceType.from_value(self.proxy.Get(NM_DEVICE_IFACE, "DeviceType"))

class NetworkManagerDeviceWired(NetworkManagerDevice):
	def __init__(self, bus, object_path):
		NetworkManagerDevice.__init__(self, bus, object_path)

	@property	
	def hwaddress(self):
		return self.proxy.Get(NM_DEVICE_WIRED_IFACE, 'HwAddress')

	@property	
	def speed(self):
		return self.proxy.Get(NM_DEVICE_WIRED_IFACE, 'Speed')

	@property	
	def carrier(self):
		return self.proxy.Get(NM_DEVICE_WIRED_IFACE, 'Carrier')

class NetworkManagerDeviceWireless(NetworkManagerDevice):
	def __init__(self, bus, object_path):
		NetworkManagerDevice.__init__(self, bus, object_path)
    
    
#class NetworkManagerAccessPoint
    

class NetworkManager(object):
	# Map of subclasses to return for different device types
	device_types = {
		DeviceType.UNKNOWN: NetworkManagerDevice,
		DeviceType.ETHERNET: NetworkManagerDeviceWired,
		DeviceType.WIFI: NetworkManagerDevice,
		DeviceType.GSM: NetworkManagerDevice,
		DeviceType.CDMA: NetworkManagerDevice,
	}
	
	def __init__(self):
		self.bus = dbus.SystemBus()
		self.proxy = self.bus.get_object(NM_NAME, NM_PATH)
		self.settings = self.bus.get_object(NM_NAME, NM_SETTINGS_PATH)

	def __repr__(self):
		return "<NetworkManager>"
	
	def get_devices(self):
		"""
		Returns a list of object paths of network devices known to the system
		"""
		devices = []
		for device_path in self.proxy.GetDevices():
			device = self.bus.get_object(NM_NAME, device_path)
			device_type = DeviceType.from_value(device.Get(NM_DEVICE_IFACE, 'DeviceType'))
			devices.append(NetworkManager.device_types[device_type](self.bus, device_path))
		return devices

	def sleep(self, sleep):
		pass
	
	def list_connections(self):
		return [NetworkManagerConnection(self.bus, path) for path in self.settings.ListConnections(dbus_interface=NM_SETTINGS_IFACE)]
		
	def add_connection(self, properties):
		self.settings.AddConnection(properties, dbus_interface=NM_SETTINGS_IFACE)
		
	def get_connection(self, path):
		return NetworkManagerConnection(self.bus, path)
		
	def get_settings(self):
		"""
		Returns a wrapper providing access to NetorkManagerSettings 
		for accessing system connection settings
		"""
		return self.settings
	
class NetworkManagerConnection():
	def __init__(self, bus, connection):
		self.proxy = bus.get_object(NM_NAME, connection);
	
	def __repr__(self):
		return "<NetworkManagerConnection: %s>" % self.get_settings()
	
	def get_settings(self):
		"""
		Returns this connections settings - a{sa{sv}} (String_String_Variant_Map_Map)
		The nested settings maps describing this object.
		"""
		return self.proxy.GetSettings(dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')

	def update(self, properties):
		self.proxy.Update(properties, dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')
		
	def delete(self):
		self.proxy.Delete(dbus_interface='org.freedesktop.NetworkManagerSettings.Connection')

