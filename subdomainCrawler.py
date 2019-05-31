#!/usr/bin/env python

import requests
import optparse


# command line args
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-d","--domain", dest="domain", help="IP address to check for domains")
    parser.add_option("-w","--wordlist", dest="wordlist", help="Wordlist file to be used for bruteforcing subdomains. One subdomain per line.")
    (options, arguments) = parser.parse_args()
    if not  options.domain and not options.wordlist:
        parser.error("[-] Please specify a domain, use --help for more info.")
    return options

# request a url and handle errors
def request(url):
    try:
        get_response = requests.get("http://" + url)
        return get_response
    except requests.exceptions.ConnectionError:
        #print("[-] Not found...")
        pass

# main program
options = get_arguments()
target_url = options.domain
wordlistPath = options.wordlist

# open wordlist file and add subdomain to the url and check if it exists
with open(wordlistPath, 'r') as wordListFile:
    for line in wordListFile:
        test_url = line.strip() + "."  + target_url
        #print("[+] Testing URL: " + test_url)
        response = request(test_url)
        if response:
            print("[+] Subdomain found: " + test_url)
            
