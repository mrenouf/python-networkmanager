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
NM_DEVICES_IFACE="org.freedesktop.NetworkManager.Devices"
NM_DEVICE_WIRED_IFACE="org.freedesktop.NetworkManager.Device.Wired"

class enum(object):	
	def __init__(self, value, desc):
		self.value = value
		self.desc = desc
		self.__class__.values[value] = self

	def __repr__(self):
		return "%s(%d, ""%s"")" % (self.__class__.__str__(self), self.value, self.desc)

	def __str__(self):
		return self.desc

	def __eq__(self, other):
		return self.value == other.value

	def __ne__(self, other):
		return self.value != other.value

	@classmethod
	def value_of(cls, value):
		return cls.values[value]

class DeviceType(enum):
	"""	
	NM_DEVICE_TYPE
	"""
	values = {"Unknown": 0, "Ethernet": 1, "Wifi": 2, "GSM": 3, "CDMA": 4}
	
	@classmethod
	def value_of(cls, desc):
		return DeviceType(cls.values[desc])
	
	@classmethod
	def value_of(cls, value):
		return cls.values[value]	
	
	def __str__(self):
		return self.__class__.values[self.value]

	def __int__(self):
		return self.value

	def __init__(self, value):
		self.value = value
	
	class Unknown(DeviceType):
		def __str__(self):
			return "Unknown"


class DeviceState(object):
	"""
	NM_DEVICE_STATE
	"""
	#The device is in an unknown state.
	UNKNOWN = 0
	#The device is not managed by NetworkManager.
	UNMANAGED = 1
	#The device cannot be used (carrier off, rfkill, etc).
	UNAVAILABLE = 2
	#The device is not connected.
	DISCONNECTED = 3
	#The device is preparing to connect.
	PREPARE = 4
	#The device is being configured.
	CONFIG = 5
	#The device is awaiting secrets necessary to continue connection.
	NEED_AUTH = 6
	#The IP settings of the device are being requested and configured.
	IP_CONFIG = 7
	#The device is active.
	ACTIVATED = 8
	#The device is in a failure state following an attempt to activate it.
	FAILED = 9

class DeviceCap(object):
	"""
	NM_DEVICE_CAP
	"""
	NONE = 0
	SUPPORTED = 1
	CARRIER_DETECT = 2

class DeviceStateReason(object):
	"""
	NM_DEVICE_STATE_REASON
	"""
	#The reason for the device state change is unknown.
	UNKNOWN = 0
	#The state change is normal.
	NONE = 1
	#The device is now managed.
	NOW_MANAGED = 2
	#The device is no longer managed.
	NOW_UNMANAGED = 3
	#The device could not be readied for configuration.
	CONFIG_FAILED = 4
	#IP configuration could not be reserved (no available address, timeout, etc).
	CONFIG_UNAVAILABLE = 5
	#The IP configuration is no longer valid.
	CONFIG_EXPIRED = 6
	#Secrets were required, but not provided.
	NO_SECRETS = 7
	#The 802.1X supplicant disconnected from the access point or authentication server.
	SUPPLICANT_DISCONNECT = 8
	#Configuration of the 802.1X supplicant failed.
	SUPPLICANT_CONFIG_FAILED = 9
	#The 802.1X supplicant quit or failed unexpectedly.
	SUPPLICANT_FAILED = 10
	#The 802.1X supplicant took too long to authenticate.
	SUPPLICANT_TIMEOUT = 11
	#The PPP service failed to start within the allowed time.
	PPP_START_FAILED = 12
	#The PPP service disconnected unexpectedly.
	PPP_DISCONNECT = 13
	#The PPP service quit or failed unexpectedly.
	PPP_FAILED = 14
	#The DHCP service failed to start within the allowed time.
	DHCP_START_FAILED = 15
	#The DHCP service reported an unexpected error.
	DHCP_ERROR = 16
	#The DHCP service quit or failed unexpectedly.
	DHCP_FAILED = 17
	#The shared connection service failed to start.
	SHARED_START_FAILED = 18
	#The shared connection service quit or failed unexpectedly.
	SHARED_FAILED = 19
	#The AutoIP service failed to start.
	AUTOIP_START_FAILED = 20
	#The AutoIP service reported an unexpected error.
	AUTOIP_ERROR = 21
	#The AutoIP service quit or failed unexpectedly.
	AUTOIP_FAILED = 22
	#Dialing failed because the line was busy.
	MODEM_BUSY = 23
	#Dialing failed because there was no dial tone.
	MODEM_NO_DIAL_TONE = 24
	#Dialing failed because there was carrier.
	MODEM_NO_CARRIER = 25
	#Dialing timed out.
	MODEM_DIAL_TIMEOUT = 26
	#Dialing failed.
	MODEM_DIAL_FAILED = 27
	#Modem initialization failed.
	MODEM_INIT_FAILED = 28
	#Failed to select the specified GSM APN.
	GSM_APN_FAILED = 29
	#Not searching for networks.
	GSM_REGISTRATION_NOT_SEARCHING = 30
	#Network registration was denied.
	GSM_REGISTRATION_DENIED = 31
	#Network registration timed out.
	GSM_REGISTRATION_TIMEOUT = 32
	#Failed to register with the requested GSM network.
	GSM_REGISTRATION_FAILED = 33
	#PIN check failed.
	GSM_PIN_CHECK_FAILED = 34
	#Necessary firmware for the device may be missing.
	FIRMWARE_MISSING = 35
	#The device was removed.
	REMOVED = 36
	#NetworkManager went to sleep.
	SLEEPING = 37
	#The device's active connection was removed or disappeared.
	CONNECTION_REMOVED = 38
	#A user or client requested the disconnection.
	USER_REQUESTED = 39
	#The device's carrier/link changed.
	CARRIER = 40
	#The device's existing connection was assumed.
	CONNECTION_ASSUMED = 41
	#The 802.1x supplicant is now available.
	SUPPLICANT_AVAILABLE = 42

class NetworkManager(object):
	def __init__(self):
		self.bus = dbus.SystemBus()
		self.proxy = self.bus.get_object(NM_NAME, NM_PATH)
		self.settings = self.bus.get_object(NM_NAME, NM_SETTINGS_PATH)
	
	def get_devices(self):
		"""
		Returns a list of object paths of network devices known to the system
		"""
		devices = []
		for device_path in self.proxy.GetDevices():
			device = self.bus.get_object(NM_NAME, device_path)
			device_type = device.Get(NM_DEVICES_IFACE, 'DeviceType')
			if (device_type == DeviceType.ETHERNET):
				devices.append(NetworkManagerDeviceWired(self.bus, device_path))
		return devices

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
	def __init__(self, bus, object_path):
		self.proxy = bus.get_object(NM_NAME, object_path)
		self.type = self.proxy.Get(NM_DEVICES_IFACE, 'DeviceType')
	
	def getattr__(self, name):
		return self.proxy.Get(NM_DEVICES_IFACE, name)

	#return self.proxy.get_dbus_method("Foo", dbus_interface='com.example.Bar')(123)
	
	def disconnect(self):
		self.proxy.Disconnect()

	@property
	def udi(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Udi")

	@property
	def interface(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Interface")

	@property
	def driver(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Driver")

	@property
	def capabilities(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Capabilities")

	@property
	def ipv4_address(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Ip4Address")

	@property
	def state(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "State")

	@property
	def ipv4config(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Ip4Config")

	@property
	def dhcp4config(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Dhcp4Config")

	@property
	def ip6config(self):
		return self.proxy.Get(NM_DEVICES_IFACE, "Ip6Config")

	@property
	def managed(self):
		"""
		Whether or not this device is managed by NetworkManager.
		"""
		return self.proxy.Get(NM_DEVICES_IFACE, "Managed")

	@property
	def type(self):
		"""
		The general type of the network device; ie Ethernet, WiFi, etc.

		TYPE_UNKNOWN
		TYPE_ETHERNET
		TYPE_WIFI
		TYPE_GSM
		TYPE_CDMA
		"""
		#return ["Unknown", "Ethernet", "Wifi", "GSM", "CDMA"][
		return self.proxy.Get(NM_DEVICES_IFACE, "Capabilities")


class NetworkManagerDeviceWired(NetworkManagerDevice):
	def __init__(self, bus, object_path):
		super(NetworkManagerDeviceWired, self).__init__(bus, object_path)
		self.proxy = bus.get_object(NM_NAME, object_path)

	def __getattr__(self, name):
		return self.proxy.Get(NM_DEVICE_WIRED_IFACE, name)

	def get_hw_address(self):
		return self.HwAddress
	
	def get_speed(self):
		return self.Speed

	def has_carrier(self):
		return self.Carrier

class NetworkManagerSettings():
	def __init__(self, bus):
		self.proxy = bus.get_object(NM_NAME, NM_SETTINGS_PATH)
		
	def list_connections(self):
		return self.proxy.ListConnections(dbus_interface=NM_SETTINGS_IFACE)
	
	def add_connection(self, properties):
		pass
	
class NetworkManagerConnection():
	def __init__(self, bus, connection):
		self.proxy = bus.get_object(NM_NAME, connection);
	
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




