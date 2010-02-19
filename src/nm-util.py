#!/usr/bin/python

import sys
from optparse import OptionParser, OptionGroup
from networkmanager import (NetworkManager, WirelessSettings, WiredSettings, 
    DeviceType, DeviceState, DeviceStateReason, DeviceCap)
from ipaddr import IPAddress, IPv4IpValidationError
import uuid
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

def parse_connection_settings(args):
    """Parses position arguments for connection settings
    
    Format is in the form of [[token] <value>, ...] where the value
    may be optional for some boolean options. Any problems are raised
    as a ValueError with a user-friendly message.
    """
    options = {"auto": True}
    pos = 0

    while pos < len(args):
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

    settings_usage = "settings: \"[auto | ip <address> mask <address> gw <address> dns <dns>]"
    
    if not options['auto']:
        if not options.has_key('ip'):
            raise ValueError("Settings: Missing value for 'ip'\n" + settings_usage)

        if not options.has_key('mask'):
            raise ValueError("Settings: Missing value for 'mask'\n" + settings_usage)
            
        if not options.has_key('gw'):
            raise ValueError("Settings: missing value for 'gw'\n" + settings_usage)

        if not options.has_key('dns'):
            raise ValueError("Settings: missing value for 'dns'\n" + settings_usage)

    return options

def list_connections(nm=NetworkManager()):
    types = {'802-3-ethernet':'Wired (Ethernet)','802-11-wireless':'Wireless (Wifi)'}
    for conn in nm.connections:
        print "UUID:     %s" % conn.settings.uuid
        print "Id:       %s" % conn.settings.id
        print "Type:     %s" % (types[conn.settings.type])
        if conn.settings.mac_address is not None:
            device = device_for_hwaddr(conn.settings.mac_address)
            print "Device:   %s" % ("Unknown" if device is None else device.interface)

        if conn.settings.auto:
            print "Address:  auto (DHCP)"
        else:
            print "Address:  %s" % conn.settings.address
            print "Netmask:  %s" % conn.settings.netmask
            print "Gateway:  %s" % conn.settings.gateway

        if conn.settings.dns is not None:
            print "DNS:     %s" % conn.settings.dns

def list_active_connections(nm=NetworkManager()):
    types = {'802-3-ethernet':'Wired (Ethernet)','802-11-wireless':'Wireless (Wifi)'}
    for active in nm.active_connections:
        print "UUID:     %s" % active.connection.settings.uuid
        print "Id:       %s" % active.connection.settings.id
        print "State:    %s" % active.state
        #print "Default:  %s" % active.default
        print "Type:     %s" % (types[active.connection.settings.type])
        print "Device:   %s" % (",".join([device.interface for device in active.devices]))
        #print "Settings from %s:" % active.service_name

        if active.connection.settings.auto:
            print "Address: auto (DHCP)"
        else:
            print "Address:  %s" % active.connection.settings.address
            print "Netmask:  %s" % active.connection.settings.netmask
            print "Gateway:  %s" % active.connection.settings.gateway

        if active.connection.settings.dns is not None:
            print "DNS:     %s" % conn.settings.dns

def create_connection(parser, options, args, nm=NetworkManager()):
    types = {
        'wired': DeviceType.ETHERNET, 
        'wireless': DeviceType.WIFI
    }

    if not options.id:
        parser.error("Create: you must supply a connection id (--id=\"MyConnection\").")

    if not options.device and not options.type:
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
        type = types[options.type]
                   
    # Create a settings object of the appropriate type
    settings = None

    if type == DeviceType.ETHERNET:
        settings = WiredSettings()
    elif type == DeviceType.WIFI:
        settings = WirelessSettings()

    settings.uuid = str(uuid.uuid4())
    
    # apply the settings        
    #print settings
    settings.id = options.id
    if device is not None:
        settings.device = device
        if type == DeviceType.ETHERNET:
            settings.mac_address = device.hwaddress
        
    try:
        params = parse_connection_settings(args)
    except ValueError, e:
        parser.error(e)
        
    if params['auto']:
        settings.set_auto()
    else:
        settings.address = params['ip']
        settings.netmask = params['mask']
        settings.gateway = params['gw']

    if params.has_key('dns'):
        settings.dns = params['dns']
    
    nm.add_connection(settings)

def modify_connection(parser, options, args, nm=NetworkManager()):
    uuid = options.ensure_value('uuid', None)
    
    if uuid is None:
        parser.error("Modify: you must supply a connection uuid " 
                     "(Use the  '--list' option to find this).")

    conn = nm.get_connection(id)
    if conn is None:
        parser.error("Modify: the uuid does not match an existing connection")       

    settings = conn.settings
    
    try:
        params = parse_connection_settings(args)
    except ValueError, e:
        parser.error(e)
        
    if params['auto']:
        settings.set_auto()
    else:
        settings.address = params['ip']
        settings.netmask = params['mask']
        settings.gateway = params['gw']
    
    if params.has_key('dns'):
        settings.dns = params['dns']

    conn.update(settings)

def delete_connection(parser, options, nm=NetworkManager()):
    uuid = options.ensure_value('uuid', None)
    
    if uuid is None:
        parser.error("Create: you must supply a connection uuid.")

    conn = nm.get_connection(uuid)
    if conn is None:
        parser.error("Delete: the uuid does not match an existing connection")       

    conn.delete()
    
def activate_connection(parser, options, nm=NetworkManager()):
    uuid = options.ensure_value('uuid', None)
    
    if uuid is None:
        parser.error("Modify: you must supply a connection uuid " 
                     "(Use the  '--list' option to find this).")

    conn = nm.get_connection(uuid)
    device = None
    
    print "Devices: %s" % nm.devices
    types = {
        DeviceType.ETHERNET: '802-3-ethernet', 
        DeviceType.WIFI: '802-11-wireless' 
    }

    for d in nm.devices:
        print d.type
        if types[d.type] == conn.settings.type:
            device = d 
            break
      
    if device is None:
        parser.error("Activate: there are no network devices " 
                     "available for this type of connection")

    nm.activate_connection(conn, device)

def deactivate_connection(parser, options, nm=NetworkManager()):
    uuid = options.ensure_value('uuid', None)
    
    if uuid is None:
        parser.error("Modify: you must supply a connection uuid " 
                     "(Use the  '--list' option to find this).")

    for active in nm.active_connections:
        if active.connection.settings.uuid == uuid:
            nm.deactivate_connection(active.proxy)
            return

def main(argv=None):
   
    if argv is None:
        argv = sys.argv

    usage = ("usage: %prog --ACTION [--uuid ID] [--name=""NAME""] [-d DEVICE] " 
             "[-t TYPE] [auto | ip <address> mask <address> gw <address> dns <dns>]")

    parser = OptionParser(usage)

    action_group = OptionGroup(parser,  
        "Action", "Specify what action to perform (choose one).")

    # Actions
    action_group.add_option("-l", "--list", 
                        action="store_const", 
                        dest="action", 
                       const="list",
                        help='List the existing connections')

    action_group.add_option("--list-active", 
                        action="store_const", 
                        dest="action", 
                        const="list-active",
                        help='List the connection which are currently active')

    action_group.add_option("--activate",
                        action="store_const",
                        dest="action",
                        const="activate",
                        help='Activate a connection (must specify ID)') 

    action_group.add_option("--deactivate",
                        action="store_const",
                        dest="action",
                        const="deactivate",
                        help='Deactivate a connection (must specify ID)') 

    action_group.add_option("--create", 
                        action="store_const", 
                        dest="action", 
                        const="create", 
                        help='Create a new connection')

    action_group.add_option("--modify", 
                        action="store_const", 
                        dest="action", 
                        const="modify",
                        help='Update a connection')

    action_group.add_option("--delete", 
                        action="store_const", 
                        dest="action", 
                        const="delete", 
                        help='Delete a connection')

    parser.add_option_group(action_group)

    details_group = OptionGroup(parser, "Details")

    # Options
    details_group.add_option("--uuid", 
                        action="store", 
                        dest="uuid",
                        help="the unique id of connection to act on (see --list)")

    details_group.add_option("--id", 
                        action="store", 
                        dest="id",
                        help="the id (name) to use for the connection")

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

    if not options.action:
        parser.error("You must specifiy an action")

    nm = NetworkManager()    

    if options.action is 'list':
        list_connections(nm)
    elif options.action is 'list-active':
        list_active_connections(nm)        
    elif options.action is 'activate':
        activate_connection(parser, options, nm)
    elif options.action is 'deactivate':
        deactivate_connection(parser, options, nm)
    elif options.action is 'create':
        create_connection(parser, options, args, nm)
    elif options.action is 'modify':
        modify_connection(parser, options, args, nm)
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
		

