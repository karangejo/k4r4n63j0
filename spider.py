#!/usr/bin/env python

import requests
import optparse
import urlparse
import re

# command line args
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-d","--domain", dest="domain", help="Full domain to be crawled. Must include http:// or https:// before the domain")
    (options, arguments) = parser.parse_args()
    if not  options.domain:
        parser.error("[-] Please specify a domain, use --help for more info.")
    return options

# extract links from a url
def extract_links(url):
    response = requests.get(url)
    return re.findall('(?:href=")(.*?)"',response.content)

# crawl a webpage looking for links recursively
def crawl(url):
    # get all links from page
    href_links = extract_links(url)
    for link in href_links:
        link = urlparse.urljoin(url, link)
        #only prints the link if it is on the same domain
        if "#" in link:
            link.split("#")[0]
        if url in link and link not in target_links:
            # appends all links to the target_link list and prints the unique links the calls itself on that link to find all links contained in that link... confusing...
            target_links.append(link)
            print(link)
            crawl(link)

# main program
options = get_arguments()
target_url = options.domain
target_links = []
# starts the main execution
crawl(target_url)
