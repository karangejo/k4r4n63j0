#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import socket
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i","--ip", dest="ip", help="IP address to check for domains")
    parser.add_option("-d","--domain", dest="domain", help="Domain to be used to  check for other domains")
    (options, arguments) = parser.parse_args()
    if not options.ip and not options.domain:
        parser.error("[-] Please specify an option, use --help for more info.")
    return options

ip = ""

options = get_arguments()
if options.domain:
    ip = socket.gethostbyname(options.domain)
elif options.ip:
    ip = options.ip

url = "http://www.bing.com/search?q=ip%3a" + ip

html_page = urllib2.urlopen(url)
soup = BeautifulSoup(html_page)
links= []

for link in soup.findAll(href=re.compile("http.*")):
    links.append(link.get('href'))

for link in links:
    if "microsoft" not in link and "http" in link:
        domain = re.search("(?:http.*?//)(.*?)(?:/)",link)
        domain_ip = socket.gethostbyname(domain.group(1))
        if domain_ip == ip:
            print("IP of " + domain.group(1) + " is " + domain_ip)
