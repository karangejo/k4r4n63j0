#!/usr/bin/env python

import subprocess
import optparse
import re

# specify all the command line arguments
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i","--interface", dest="interface", help="Interface to change MAC address or to restore")
    parser.add_option("-m","--mac", dest="new_mac", help="New MAC address to be used. Does not need to be set if restoring to original MAC")
    parser.add_option("-r","--restore",dest="restore", help="(Optional) Restore default MAC if set to True")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info")
    if options.restore:
        return options
    elif not options.new_mac:
        parser.error("[-] Please specify a new MAC address, use --help for more info")
    return options

# change the mac address through system calls to ifconfig
def change_mac(interface,new_mac):
    print("[+] Changing MAC address for " + interface + " to " + new_mac)
    subprocess.call(["ifconfig",interface,"down"])
    subprocess.call(["ifconfig",interface,"hw","ether",new_mac])
    subprocess.call(["ifconfig",interface,"up"])

# restore the original mac address
def restore_mac(interface):
    ethtool_result = subprocess.check_output(["ethtool","-P",interface])
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w",ethtool_result)
    change_mac(interface,mac_address_search_result.group(0))


# get the current mac address using regexp search from ifconfig
def get_current_mac(interface):
    ifconfig_result = subprocess.check_output(["ifconfig",options.interface])
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)
    if mac_address_search_result:
        return mac_address_search_result.group(0)
    else:
        print("[-] Could not read MAC addresss from interface")


# main program

options = get_arguments()  # get arguments from commandline

# print the currrent mac address
current_mac = get_current_mac(options.interface) 
print("[+] Current MAC address for " + options.interface +" is " + current_mac)

# if the -r or --restore option is present then reset the mac to the original one
if options.restore:
    restore_mac(options.interface)

# else change the mac address according to the options specified
else:
    change_mac(options.interface,options.new_mac)
    current_mac = get_current_mac(options.interface)
    
    # check if the mac address really did change 
    if current_mac == options.new_mac:
        print("[+] MAC address was successfully changed to " + current_mac)
    else:
        print("[-] MAC address was not sucessfully changed")


