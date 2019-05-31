#!/usr/bin/env python

import requests
import optparse

# get command line arguments
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-d","--domain", dest="domain", help="IP address to check for domains")
    parser.add_option("-w","--wordlist", dest="wordlist", help="Wordlist file to be used for bruteforcing subdomains. One subdomain per line.")
    (options, arguments) = parser.parse_args()
    if not  options.domain and not options.wordlist:
        parser.error("[-] Please specify a domain, use --help for more info.")
    return options

# safely request a url and handle errors when requesting a non-existent one
def request(url):
    try:
        get_response = requests.get("http://" + url)
        return get_response
    except requests.exceptions.ConnectionError:
        #print("[-] Not found...")
        pass

# get args
options = get_arguments()
target_url = options.domain
wordlistPath = options.wordlist

# open the wordlist path loop over the lines and test out the directory URLs
with open(wordlistPath, 'r') as wordListFile:
    for line in wordListFile:
        test_url = target_url + "/" + line.strip()
        #print("[+] Testing URL: " + test_url)
        response = request(test_url)
        if response:
            print("[+] Directory found: " + test_url)
            
