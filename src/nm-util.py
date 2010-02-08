#!/usr/bin/python

import sys
from optparse import OptionParser
from networkmanager import NetworkManager, DeviceType, DeviceState, DeviceStateReason, DeviceCap

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser()
    parser.add_option("-l", "--list", action="store_const", dest="action", const="list", help="list connections")

    (options, args) = parser.parse_args()

    nm = NetworkManager()
    types = {'802-3-ethernet':'Wired (Ethernet)','802-11-wireless':'Wireless (Wifi)'}
    if options.action == "list":
        for conn in nm.connections:
            print "[%s]" % conn.settings.id
            print     "Type:    %s" % (types[conn.settings.type])
            if conn.settings.auto:
                print "Address: AUTO (dhcp)"
            else:
                print "Address: %s" % conn.settings.address
                print "Netmask: %s" % conn.settings.netmask
                print "Gateway: %s" % conn.settings.gateway
            
            if conn.settings.dns is not None:
                print "DNS:     %s" % conn.settings.dns
                
    else:
        parser.print_usage()

if __name__ == "__main__":
    sys.exit(main())

# --enable --disable
# --new-profile 'name'
# --edit-profile --auto
# --edit-profile --manual --

# -e <name> --manual <ip> <mask> <gw> 
# -e <name>


#    print "===Devices==="
#    for device in nm.get_devices():
#        print device
#        print device.hwaddress
#        if device.state == DeviceState.ACTIVATED:
#           print device.ip4config

#    print "===Connections==="
#    for conn in nm.connections:
#        print conn.settings
#        print conn.settings.mac_address
#        print conn.settings.address

        
#    print "===Active==="
#    for active in nm.active_connections:
#        print active.connection
#        print active.connection.settings

#if __name__ == "__main__":
#    main(sys.argv)	
		

