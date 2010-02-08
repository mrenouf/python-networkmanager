#!/usr/bin/python

import sys
from networkmanager import NetworkManager, DeviceType, DeviceState, DeviceStateReason, DeviceCap

def main(argv=None):
    if argv is None:
        argv = sys.argv

    nm = NetworkManager()

    print "===Devices==="
    for device in nm.get_devices():
        print device
        print device.hwaddress
        if device.state == DeviceState.ACTIVATED:
            print device.ip4config

    print "===Connections==="
    for conn in nm.connections:
        print conn.settings
        print conn.settings.mac_address
        print conn.settings.address

        
    print "===Active==="
    for active in nm.active_connections:
        print active.connection
        print active.connection.settings

if __name__ == "__main__":
    main(sys.argv)	
		

