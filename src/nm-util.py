#!/usr/bin/python

import sys
from optparse import OptionParser, OptionGroup
from networkmanager import (NetworkManager, WirelessSettings, WiredSettings, 
    DeviceType, DeviceState, DeviceStateReason, DeviceCap)
from ipaddr import IPAddress, IPv4IpValidationError

nm = None

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def is_ethernet(connection):
    return connection.settings.type == '802-3-ethernet'

def is_wifi(connection):
    return connection.settings.type == '802-11-wireless'

def device_for_hwaddr(hwaddr, nm=NetworkManager()):
    for device in nm.devices:
        if device.hwaddress == hwaddr:
            return device

def connections_for_device(device, nm=NetworkManager()):
    hwaddr = None
    for device in nm.devices:
        if device.interface == device:
            hwaddr = device.hwaddr
            break
    if hwaddr is None:
        return None
        
    conns = []
    for conn in nm.connections:
        if conn.settings.mac_address == hwaddr:
            conns.append(conn)
    return conns

def find_active_devices(nm=NetworkManager()):
    devices = []
    for conn in nm.active_connections:
        for device in conn.devices:
            devices.append(device)
    return devices
    
 #   [active if active.connection.settings.type in [ in nm.active_connections]
    

#    for conn in nm.active_connections:
#        print conn
#        print conn.devices.

#    wired = filter(is_wired_connection, nm.connections)

def parse_connection_settings(args):
    """Parses position arguments for connection settings
    
    Format is in the form of [[token] <value>, ...] where the value
    may be optional for some boolean options. Any problems are raised
    as a ValueError with a user-friendly message.
    """
    options = {"auto": True}
    pos = 0

    while pos < len(args):
        print pos
        opt = args[pos]
        if not opt in ['ip','mask','gw','dns']:
            raise ValueError("Invalid option '%s'" % (opt))

        if opt != "auto":
            pos += 1
            # The rest of these require a value in the next position
            if pos == len(args):
                raise ValueError("Missing value for option '%s'" % (opt))

            value = args[pos]    
            try:
                if opt  == "dns":
                    options['dns'] = IPAddress(value,version=4)
                else:
                    if opt == "ip":
                        options['ip'] = IPAddress(value,version=4)
                    elif opt  == "mask":
                        options['mask'] = IPAddress(value,version=4)
                    elif opt  == "gw":
                        options['gw'] = IPAddress(value,version=4)

                    options['auto'] = False

            except IPv4IpValidationError, e:
                raise ValueError("Invalid value for '%s': %s" % (opt, e))
                                
        pos += 1

    if not options['auto']:
        if not options.has_key('ip'):
            raise ValueError("Settings: Missing value for 'ip'\n"
            "settings: \"ip <address> mask <address> gw <address>\"")

        if not options.has_key('mask'):
            raise ValueError("Settings: Missing value for 'mask'\n"
            "settings: \"ip <address> mask <address> gw <address>\"")
            
        if not options.has_key('gw'):
            raise ValueError("Settings: missing value for 'gw'\n"
            "settings: \"[auto | ip <address> mask <address> gw <address>]\"")
    return options


def list_connections(nm=NetworkManager()):
    types = {'802-3-ethernet':'Wired (Ethernet)','802-11-wireless':'Wireless (Wifi)'}
    for conn in nm.connections:
        print "ID:      \"%s\"" % conn.settings.id
        print "Type:    %s" % (types[conn.settings.type])
        if conn.settings.mac_address is not None:
            device = device_for_hwaddr(conn.settings.mac_address)
            print "Device:  %s" % ("Unknown" if device is None else device.interface)

        if conn.settings.auto:
            print "Address: auto (DHCP)"
        else:
            print "Address: %s" % conn.settings.address
            print "Netmask: %s" % conn.settings.netmask
            print "Gateway: %s" % conn.settings.gateway

                
        if conn.settings.dns is not None:
            print "DNS:     %s" % conn.settings.dns

        print conn.settings._settings
        print "----------------------"

def create_connection(parser, options, args, nm=NetworkManager()):

    print options.__class__
    if not options.ensure_value('id', False):
        parser.error("Create: you must supply a connection id.")
    
    if not options.ensure_value('device', False) and not options.ensure_value('type', False):
        parser.error("Create: you must specify a device name or connection type.")

    device = None
    # find the device with the specified interface name ('eth0', etc)
    if options.device:
        for d in nm.devices:
            if d.interface == options.device:
                device = d

    # if a device was specified, create a connection of the same type
    # otherwise use the type that was supplied through the 'type' option
    if device is not None:
        type = device.type
    else:
        type = options.type
                   
    # Create a settings object of the appropriate type
    settings = None
    print "Type: %s" % (type)
    if type == 'wired':
        settings = WiredSettings()
    elif type == 'wireless':
        settings = WirelessSettings()

    # apply the settings        
    print settings
    settings.id = options.id
    if device is not None:
        settings.device = device
        
    try:
        params = parse_connection_settings(args)
    except ValueError, e:
        parser.error(e)
        
    print params
    if params['auto']:
        settings.set_auto()
    else:
        settings.address = params['ip']
        settings.netmask = params['mask']
        settings.gateway = params['gw']

    if params.has_key('dns'):
        settings.dns = params['dns']

    nm.add_connection(settings)

def update_connection(parser, options, args, nm=NetworkManager()):
    if not options.id:
        parser.error("Create: you must supply a connection id.")

def delete_connection(parser, options, nm=NetworkManager()):
    if not options.id or options.device:
        parser.error("Delete: you must supply a connection id or device name.")

def enable_connection(parser, options, nm=NetworkManager()):
    pass

def disable_connection(parser, options, nm=NetworkManager()):
    pass


def determine_connection(parser, options, nm=NetworkManager()):
    types = {'wired': '802-3-ethernet', 'wireless': '802-11-wireless'}
    id = options.id
    dev = options.device
    type = options.type

    id_conn = []
    if options.id is not None:
        conn = [conn for conn in nm.connections if conn.id is id]
        if len(conn) is 0:
            # no connection with this id exists
            parser.error("Invalid connection id '%s'" % (options.id))

    dev_conn = []
    if dev is not None:
        dev_conn = connections_for_device(dev, nm)

    type = None
    if options.type is not None:
        type = types[options.type]

    # neither connection id or device specified
    if not options.id and not options.device:
        parser.error("A connection id or device must be specified.")

    # no connections found
    if len(id_conn) == 0 and len(dev_conn) == 0:
        if not options.device:
            parser.error("There are no connections with the id '%s'" % (options.id))
        if not options.id:
            parser.error("There are no connections associated with the device '%s'" % (options.device))

    # only deivice specified and found more than one connection       
    if len(id_conn) == 0 and len(dev_conn) > 1 and not options.id:
        parser.error("There is more than one connection associated with the specified device. The connection id must be specified.")   


    # both id and device specified
    if options.id and options.device:
        # find all connections from both sets with the same ids
        connections = [conn for conn in id_conn if conn.id in [conn.id for conn in dev_conn]]
        if (len(conncetions) == 0):
            parser.error("The connection id '%s' is not associated with device '%s'", (id, dev))
    
    # finally if type was specified, filter on that
    #if options.type:
        #    wired = filter(is_wired_connection, nm.connections)


        


#def create_connection(options, args, nm=NetworkManager()):
#    if options.device:   
#    if options.id:
    
    

def main(argv=None):
    #print find_active_devices()
    
    if argv is None:
        argv = sys.argv

    usage = ("usage: %prog --ACTION [--id=\"ID\"] [-d DEVICE] [-t TYPE] [auto | ip <address> mask <address> gw <address>]")

    parser = OptionParser(usage)

    action_group = OptionGroup(parser,  
        "Action", "Specify what action to perform.")

    # Actions
    action_group.add_option("-l", "--list", 
                        action="store_const", 
                        dest="action", 
                       const="list",
                        help='List the existing connections')

    action_group.add_option("--create", 
                        action="store_const", 
                        dest="action", 
                        const="create", 
                        help='Create a new connection')

    action_group.add_option("--update", 
                        action="store_const", 
                        dest="action", 
                        const="update",
                        help='Update a connection')

    action_group.add_option("--delete", 
                        action="store_const", 
                        dest="action", 
                        const="delete", 
                        help='Delete a connection')

    action_group.add_option("--enable", 
                        action="store_const", 
                        dest="action", 
                        const="enable", 
                        help='Enable a connection')

    action_group.add_option("--disable", 
                        action="store_const", 
                        dest="action", 
                        const="disable", 
                        help='Disable a connection')

    parser.add_option_group(action_group)

    details_group = OptionGroup(parser, "Details")

    # Options
    details_group.add_option("--id", 
                        action="store", 
                        dest="id",
                        help="the connection to act on (see --list)")

    details_group.add_option("-t", 
                        choices=['wired','wireless'], 
                        action="store",
                        dest="type",   
                        help="the connection type [wired|wireless]")

    details_group.add_option("-d", 
                        action="store", 
                        dest="device", 
                        help="the network device to act on (ethX, wlanX, etc)")

    parser.add_option_group(details_group)

    (options, args) = parser.parse_args()
    print args

    if not options.action:
        parser.error("You must specifiy an action")

    nm = NetworkManager()    

    if options.action is 'list':
        list_connections(nm)
    elif options.action is 'create':
        create_connection(parser, options, args, nm)
    elif options.action is 'update':
        update_connection(parser, options, args, nm)
    elif options.action is 'delete':
        delete_connection(parser, options, nm)
    elif options.action is 'enable':
        enable_connection(parser, options, nm)
    elif options.action is 'disable':
        disable_connection(parser, options, nm)
    else:
        parser.print_usage()


if __name__ == "__main__":
    sys.exit(main())
		

