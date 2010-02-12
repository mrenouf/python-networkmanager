#!/usr/bin/python

import glib
import gtk
import dbus
import enum
import socket
import uuid
import ipaddr

from binascii import unhexlify

ETH="802-3-ethernet"

NM_NAME="org.freedesktop.NetworkManager"
NM_PATH="/org/freedesktop/NetworkManager"

NM_DEVICE="org.freedesktop.NetworkManager.Device"
NM_DEVICE_WIRED="org.freedesktop.NetworkManager.Device.Wired"
NM_DEVICE_WIRELESS="org.freedesktop.NetworkManager.Device.Wireless"
NM_CONN_ACTIVE="org.freedesktop.NetworkManager.Connection.Active"

NM_SETTINGS_NAME="org.freedesktop.NetworkManagerSettings"
NM_SETTINGS_PATH="/org/freedesktop/NetworkManagerSettings"
NM_SETTINGS_CONNECTION="org.freedesktop.NetworkManagerSettings.Connection"

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
    FAILED = 9,
)

ActiveConnectionState = enum.new("ActiveConnectionState",
    #The active connection is in an unknown state.
    UNKNOWN = 0,
    #The connection is activating.
    ACTIVATING = 1,
    #The connection is activated.
    ACTIVATED = 2,
)

DeviceCap = enum.new("DeviceCap", 
    NONE = 0,
    SUPPORTED = 1,
    CARRIER_DETECT = 2,
)

# NM_802_11_MODE
WifiMode = enum.new("WifiMode",
    #Mode is unknown.
    UNKNOWN = 0,
    #Uncoordinated network without central infrastructure.
    ADHOC = 1,
    #Coordinated network with one or more central controllers.
    INFRA = 2,
)

# NM_DEVICE_STATE_REASON
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

class Device(object):
    def __new__(cls, bus, path):
        _subclasses = { 
            DeviceType.ETHERNET: DeviceWired,
            DeviceType.WIFI: DeviceWireless,
        }
                
        device = bus.get_object(NM_NAME, path)        
        type = DeviceType.from_value(device.Get(NM_DEVICE, 'DeviceType'))
        try:
            cls = _subclasses[type]
        except KeyError:
            cls = Device
        
        return object.__new__(cls)
    
    def __init__(self, bus, object_path):
        self.proxy = bus.get_object(NM_NAME, object_path)
    
    def __repr__(self):
        return "<Device: %s [%s]>" % (self.interface, self.hwaddress)
        
    def disconnect(self):
        self.proxy.Disconnect()

    @property
    def udi(self):
        return self.proxy.Get(NM_DEVICE, "Udi")

    @property
    def interface(self):
        return self.proxy.Get(NM_DEVICE, "Interface")

    @property
    def driver(self):
        return self.proxy.Get(NM_DEVICE, "Driver")

    @property
    def capabilities(self):
        return DeviceCap.from_value(self.proxy.Get(NM_DEVICE, "Capabilities"))

    @property
    def ipv4_address(self):
        return self.proxy.Get(NM_DEVICE, "Ip4Address")

    @property
    def state(self):
        return DeviceState.from_value(self.proxy.Get(NM_DEVICE, "State"))

    @property
    def ip4config(self):
        return self.proxy.Get(NM_DEVICE, "Ip4Config")

    @property
    def dhcp4config(self):
        return self.proxy.Get(NM_DEVICE, "Dhcp4Config")

    @property
    def ip6config(self):
        return self.proxy.Get(NM_DEVICE, "Ip6Config")

    @property
    def managed(self):
        return self.proxy.Get(NM_DEVICE, "Managed")

    @property
    def type(self):
        return DeviceType.from_value(self.proxy.Get(NM_DEVICE, "DeviceType"))

class DeviceWired(Device):
    def __init__(self, bus, object_path):
        Device.__init__(self, bus, object_path)

    @property    
    def hwaddress(self):
        return self.proxy.Get(NM_DEVICE_WIRED, 'HwAddress')

    @property    
    def speed(self):
        return self.proxy.Get(NM_DEVICE_WIRED, 'Speed')

    @property    
    def carrier(self):
        return self.proxy.Get(NM_DEVICE_WIRED, 'Carrier')


class DeviceWireless(Device):
    def __init__(self, bus, object_path):
        Device.__init__(self, bus, object_path)

    @property
    def access_points(self):
        return [AccessPoint(self.bus, path) 
        for path in self.proxy.GetAccessPoints(dbus_interface=NM_DEVICE_WIRELESS)]
    
    @property
    def hwaddress(self):
        return self.proxy.Get(NM_DEVICE_WIRELESS, "HwAddress")
        
    @property
    def mode(self):
        return WifiMode.from_value(self.proxy.Get(NM_DEVICE_WIRELESS, "Mode"))

    @property    
    def bitrate(self):
        return self.proxy.Get(NM_DEVICE_WIRELESS, "Bitrate")

    @property    
    def active_access_point(self):
        return self.proxy.Get(NM_DEVICE_WIRELESS, "ActiveAccessPoint")

    @property    
    def wireless_capabilities(self):
        return self.proxy.Get(NM_DEVICE_WIRELESS, "WirelessCapabilities")

class AccessPoint(object):
    def __init__(self, bus, path):
        self.proxy = bus.get_object(NM_NAME, path)

    @property
    def flags(self):    
        pass
    
    @property
    def wpaflags(self):
        pass
        
    @property
    def rsnflags(self):
        pass
        
    @property
    def ssid(self):
        pass
        
    @property
    def frequency(self):
        pass
        
    @property
    def hwaddress(self):
        pass
        
    @property
    def mode(self):
        pass
    
    @property
    def maxbitrate(self):
        pass
        
    @property
    def strength(self):
        pass


class NetworkManager(object):
    # Map of subclasses to return for different device types
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.proxy = self.bus.get_object(NM_NAME, NM_PATH)
        self.settings = self.bus.get_object(NM_NAME, NM_SETTINGS_PATH)
    
    def __repr__(self):
        return "<NetworkManager>"
    
    def sleep(self, sleep):
        pass

    @property
    def devices(self):
        """
        Returns a list of object paths of network devices known to the system
        """
        return [Device(self.bus, path) for path in self.proxy.GetDevices()]
    
    @property
    def connections(self):
        return [Connection(self.bus, path) 
        for path in self.settings.ListConnections(dbus_interface=NM_SETTINGS_NAME)]

    @property    
    def active_connections(self):
        return [ActiveConnection(self.bus, path) 
        for path in self.proxy.Get(NM_SETTINGS_CONNECTION, "ActiveConnections")]

    def add_connection(self, settings):
        print settings._settings
        self.settings.AddConnection(settings._settings, dbus_interface=NM_SETTINGS_NAME)
        
class ActiveConnection():
    def __init__(self, bus, path):
        self.bus = bus
        self.proxy = bus.get_object(NM_NAME, path)

    def __repr__(self):
        return "<ActiveConnection: %s>" % self.connection.settings.id
        
    @property
    def service_name(self):
        return self.proxy.Get(NM_CONN_ACTIVE, "ServiceName")

    @property
    def connection(self):
        path = self.proxy.Get(NM_CONN_ACTIVE, "Connection")
        return Connection(self.bus, path)        

    @property
    def specific_object(self):
        return self.proxy.Get(NM_CONN_ACTIVE, "SpecificObject")

    @property
    def devices(self):
        return [Device(self.bus, path) for path in self.proxy.Get(NM_CONN_ACTIVE, "Devices")]

    @property
    def state(self):
        return ActiveConnectionState.from_value(
            self.proxy.Get(NM_CONN_ACTIVE, "State"))

    @property
    def default(self):
        return self.proxy.Get(NM_CONN_ACTIVE, "Default")

    @property
    def vpn(self):
        return self.proxy.Get(NM_CONN_ACTIVE, "Vpn")
    
class Connection():
    def __init__(self, bus, path):
        self.proxy = bus.get_object(NM_NAME, path);
    
    def __repr__(self):
        return "<Connection: \"%s\">" % self.settings.id
    
    @property
    def settings(self):
        """
        Returns this connections settings - a{sa{sv}} (String_String_Variant_Map_Map)
        The nested settings maps describing this object.
        """
        return Settings(self.proxy.GetSettings(dbus_interface=NM_SETTINGS_CONNECTION))

    def update(self, settings):
        """
        Update the connection to reflect the current values within the specified
        settings object (must be a subclass of Settings
        """
        self.proxy.Update(settings._settings, dbus_interface=NM_SETTINGS_CONNECTION)
        
    def delete(self):
        """ Removes this connection """
        self.proxy.Delete(dbus_interface=NM_SETTINGS_CONNECTION)


class UnsupportedConnectionType(Exception):
    """ Encountered an unknown value within connection->type """

_default_settings_wired = dbus.Dictionary({
    'connection': dbus.Dictionary({
        'type': '802-3-ethernet', 
    }), 
    '802-3-ethernet': dbus.Dictionary({
        'duplex':'full',
    }),
    'ipv4': dbus.Dictionary({
        'routes': dbus.Array([], signature='au'),
        'addresses': dbus.Array([], signature='au'),
        'dns': dbus.Array([],signature='u'),
        'method': 'auto',
    }),
    'ipv6': dbus.Dictionary({
        'routes': dbus.Array([], signature='(ayuayu)'),
        'addresses': dbus.Array([], signature='(ayu)'),
        'dns': dbus.Array([],signature='ay'),
        'method': 'ignore',
    })
})

_default_settings_wireless = dbus.Dictionary({
    'connection': dbus.Dictionary({
        'type': '802-11-wireless', 
    }), 
    '802-11-wireless': dbus.Dictionary({}),
    'ipv4': dbus.Dictionary({
        'routes': dbus.Array([], signature='au'),
        'addresses': dbus.Array([], signature='au'),
        'dns': dbus.Array([],signature='u'),
        'method': 'auto',
    }),
    'ipv6': dbus.Dictionary({
        'routes': dbus.Array([], signature='(ayuayu)'),
        'addresses': dbus.Array([], signature='(ayu)'),
        'dns': dbus.Array([],signature='ay'),
        'method': 'ignore',
    })
})

def Settings(settings):        
    try:
        conn_type = settings['connection']['type']
    except KeyError:
        raise UnsupportedConnectionType("settings: connection.type is missing")
    
    if conn_type == "802-3-ethernet":
        return WiredSettings(settings)
    elif conn_type == "802-11-wireless":
        return WirelessSettings(settings)
    else:
        raise UnsupportedConnectionType("Unknown connection type: '%s'" % conn_type)    

class BaseSettings(object):

    _ALL_ONES = all_ones = (2**32) - 1

    def __init__(self, settings):
        self._settings = settings
        self.conn_type = settings['connection']['type']
        self._settings['connection']['uuid'] = str(uuid.uuid4())
        
    def __repr__(self):
        return "<Settings>"    


    def _has_address(self):
        """
        Internal function

        Returns True if there is at least one address assigned
        within this connection. No adddresses usually indicates
        autoconfiguration
        """
        return len(self._settings['ipv4']['addresses']) > 0

    def _get_first_address(self):
        """
        Internal function
        
        Returns the first 'address' defined which is actually 
        an (address, maskbits, gateway) triplet within an array.
        
        If an address is not defined, one is created, assigned and returned.
        
        Note: Does not support multiple addresses on a single connection.
        """
        addresses = self._settings['ipv4']['addresses']
        if len(addresses) == 0:
            addresses = dbus.Array([dbus.Array([dbus.UInt32(0), dbus.UInt32(0), dbus.UInt32(0)], signature='u')], signature='au')
            self._settings['ipv4']['addresses'] = addresses
        return addresses[0] # NOTE: only reports from first address!          

    @property
    def id(self):
        """ The 'id' or name of the connection """
        return self._settings['connection']['id']

    @id.setter
    def id(self, value):
        self._settings['connection']['id'] = value
    
    @property
    def type(self):
        """ The connection type (usually indicates media standard) """
        return self._settings['connection']['type']

    @property
    def mac_address(self):
        """ The mac address of the connection if only a specific adapter should be used """
        eth = self._settings[self.conn_type]
        if not eth.has_key('mac-address'): return None
        address = self._settings[self.conn_type]['mac-address']
        return ":".join([("%02X" % int(value)) for value in address])

    @mac_address.setter
    def mac_address(self, address):
        if address is None:
            del self._settings[self.conn_type]['mac-address']
        else:
            bytes = [unhexlify(v) for v in address.split(":")]
            self._settings[self.conn_type]['mac-address'] = dbus.Array(bytes, signature='y')

    @property
    def auto(self):
        """ Return True if this connection uses network autoconfiguration """
        return self._settings['ipv4']['method'] == 'auto'
            
    def set_auto(self):
        """ Configure this connection for network autoconfiguration """
        self._settings['ipv4'] = {
            'routes': dbus.Array([], signature='au'),
            'addresses': dbus.Array([], signature='au'),
            'dns': dbus.Array([], signature='u'),
            'method': 'auto',}

    @property
    def address(self):
        """
        Returns the IPv4 address assigned to this connection in
        dotted-quad notation, or None if the connection has no
        statically assigned address information.
        """
        if not self._has_address():
            return None
    
        entry = self._get_first_address()
        return str(ipaddr.IPAddress(socket.ntohl(entry[0]), version=4))
        
    @address.setter
    def address(self, address):
        """
        Assigns an address to this connection. This also implicitly sets
        the mode to manual (disables network autoconfiguration).
        """
        entry = self._get_first_address()
        entry[0] = dbus.UInt32(socket.htonl(int(ipaddr.IPAddress(address, version=4))))
        self._settings['ipv4']['method'] = 'manual'

    @property
    def netmask(self):
        """
        Returns the network mask of the connection in dotted quad
        notation, or None if the connection has no statically assigned 
        address information.
        """
        if not self._has_address():
            return None
            
        entry = self._get_first_address()
        prefixlen = int(entry[1])
        netmask_int = self._ALL_ONES ^ (self._ALL_ONES >> prefixlen)
        return str(ipaddr.IPAddress(netmask_int))
    
    @netmask.setter
    def netmask(self, netmask):
        """
        Assigns the network mask for thisconnection. This also implicitly
        sets the mode to manual (disables network autoconfiguration).
        """
        mask=32
        ip_int = int(ipaddr.IPAddress(netmask))
        while mask:
            if ip_int & 1 == 1:
                break
            ip_int >>= 1
            mask -= 1

        return mask

        entry = self._get_first_address()
        entry[1] = dbus.UInt32(mask)
        self._settings['ipv4']['method'] = 'manual'
        
    @property
    def gateway(self):
        """
        Returns the IPv4 gateway assigned to this connection in
        dotted-quad notation, or None if the connection has no
        statically assigned address information.
        """
        if not self._has_address():
            return None

        entry = self._get_first_address()
        return str(ipaddr.IPAddress(socket.ntohl(entry[2]), version=4))
        
    @gateway.setter
    def gateway(self, gateway):
        """
        Assigns a gateway to this connection. This also implicitly sets
        the mode to manual (disables network autoconfiguration).
        """
        entry =self._get_first_address()
        entry[2] = dbus.UInt32(socket.htonl(int(ipaddr.IPAddress(gateway, version=4))))
        self._settings['ipv4']['method'] = 'manual'

    @property
    def dns(self):
        """
        The assigned DNS server if the connection is manually configured
        or autoconfiguration should be forced to use a specific DNS server.
        
        Only accesses the first DNS address defined
        """
        if len(self._settings['ipv4']['dns']) == 0:
            return None
        else:
            return str(ipaddr.IPAddress(socket.ntohl(self._settings['ipv4']['dns'][0])))

    @dns.setter
    def dns(self, address):                
        self._settings['ipv4']['dns'] = [socket.htonl(int(ipaddr.IPAddress(address)))]

class WirelessSettings(BaseSettings):
    def __repr__(self):
        return "<WirelessSettings (%s)>" % ("DHCP" if self.auto else "Static")

    def __init__(self, properties=_default_settings_wireless):
        super(WirelessSettings, self).__init__(properties)

class WiredSettings(BaseSettings):        
    def __repr__(self):
        return "<WiredSettings (%s)>" % ("DHCP" if self.auto else "Static")
        
    def __init__(self, properties=_default_settings_wired):
        super(WiredSettings, self).__init__(properties)
        
    @property        
    def duplex(self):
        return self._settings['802-3-ethernet']['duplex']

    @duplex.setter
    def duplex(self, value):
        self._settings['802-3-ethernet']['duplex'] = value

