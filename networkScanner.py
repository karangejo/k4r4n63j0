#!/usr/bin/env python

import scapy.all as scapy
import optparse

# get the commmand line arguments
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-r","--range",dest="range",help="Range of IP addresses to scan")
    (options, arguments) = parser.parse_args()
    if not options.range:
        parser.error("[-] Please enter an IP range, use --help for more info")
    else:
        return options

# scan an ip range
def scan(ip):
    # broadcast the arp requests and get the responses
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]
    
    # make a list containing ips and mac addresses and return the list
    clients_list = []
    for element in answered_list:
        client_dict = {"ip":element[1].psrc,"mac":element[1].hwsrc}
        clients_list.append(client_dict)
        
    return clients_list

# print the results with nice formatting
def print_results(result_list):
    print("--------------------------------------")
    print("|  IP\t\t\tMAC address  |")
    print("-------------------------------------------")
    for client in result_list:
        print("| " + client["ip"] + "\t\t" + client["mac"] +" |")
        print("-------------------------------------------")

# main program calls the functions
options = get_arguments()
scan_results = scan(options.range)
print_results(scan_results)
