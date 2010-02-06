#!/usr/bin/python

import sys
from networkmanager import NetworkManager, DeviceType, DeviceState, DeviceStateReason, DeviceCap

def main(argv=None):
	if argv is None:
		argv = sys.argv

	nm = NetworkManager()

    for device in nm.get_devices():
        print device.type
        print device.interface
        print device.driver
        print device.state
        if (device.type == DeviceType.ETHERNET):
            print device.speed
            print device.carrier
            print device.hwaddress
            
    for conn in nm.list_connections():
        print conn.get_settings()['connection']['id']
        print conn.get_settings()['connection']['type']


#	print "=========="
#	con = NetworkManagerConnection(bus, set.list_connections()[0])

#	set = con.get_settings()
#	print "Type: %s" % set['connection']['type']
#	print "UUID: %s" % set['connection']['uuid']
#	print "Connection %s: " % set['connection']['id']
#	print "Routes: %s" % set['ipv4']['routes']
#	print "Addresses: %s" % set['ipv4']['addresses']
#	print "DNS: %s" % set['ipv4']['dns']
#	print "Method: %s" % set['ipv4']['method']


	#set['ipv4']['dns'] = dbus.Array([dbus.UInt32(134744073)])
	#con.update(set)
	#print set
	#['802-3-ethernet']['mac-address']
	#for k in con.get_settings().keys():
	#	for v in k.keys():
	#		print v

if __name__ == "__main__":
	main(sys.argv)	
		

