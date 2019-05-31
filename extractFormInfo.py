#!/usr/bin/env python

import requests
from BeautifulSoup import BeautifulSoup
import optparse
import urlparse

# get command line args
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-d","--domain", dest="domain", help="Domain to investigate.")
    (options, arguments) = parser.parse_args()
    if not  options.domain:
        parser.error("[-] Please specify a domain, use --help for more info.")
    return options

# request url and handle errors
def request(url):
    try:
        get_response = requests.get(url)
        return get_response
    except requests.exceptions.ConnectionError:
        #print("[-] Not found...")
        pass

# main program
options = get_arguments()
target_url = options.domain
response = request(target_url)
# find all forms
parsed_html = BeautifulSoup(response.content)
forms_list = parsed_html.findAll("form")

# loop through forms
for form in forms_list:
    # print the action and the method of the form
    action = form.get("action")
    print("[+] Action: ",action)
    post_url = urlparse.urljoin(target_url, action)
    method = form.get("method")
    print("[+] Method: ",method)
    
    # initialize some variables
    post_data = {}
    inputs_list = form.findAll("input")

    # for each data input field that is of type text of the form insert a "test" and try to post it
    for inputs in inputs_list:
        input_name = inputs.get("name")
        print("[+] Input name: ", input_name)
        input_type = inputs.get("type")
        print("[+] Input type: ", input_type)
