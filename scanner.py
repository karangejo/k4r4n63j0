#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
import urlparse
import re
import requests

# Scanner class to be used with vulnerability scanner
class Scanner:

    # initialize a domain url
    def __init__(self,url):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []

    # extract all links
    def extract_links(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"',response.content)

    # recursively extract all links from the same domain and save them to self.target_links list
    def crawl(self, url=None):
        if url == None:
            url = self.target_url
        href_links = self.extract_links( url)
        for link in href_links:
            link = urlparse.urljoin(url, link)
            #only prints the link if it is on the same domain
            if "#" in link:
                link.split("#")[0]
            if url in link and link not in self.target_links:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        # find all forms
        parsed_html = BeautifulSoup(response.content)
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        print("[+] Action: " + action)
        post_url = urlparse.urljoin(target_url, action)
        method = form.get("method")
        print("[+] Method: " + method)

        # initialize some variables
        post_data = {}
        inputs_list = form.findAll("input")

        # for each data input field that is of type text of the form insert a "test" and try to post it
        for inputs in inputs_list:
            input_name = inputs.get("name")
            print("[+] Input name: " + input_name)
            input_type = inputs.get("type")
            print("[+] Input type: " + input_type)
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if method == "post":
            return requests.post(post_url, data=post_data)
        return requests.get(post_url, params=post_data)

    # run the vulnerability methods on each link and each form in each link
    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for forms in forms:
                print("[+] Testing form in: " + link)
                is_vuln_xss = self.test_xss_in_form(form, link)
                if is_vuln_xss:
                    print("[****] XSS discovered in " + link )
                    print("[****] Check out the following form for exploit:")
                    print(form)
            if "=" in link:
                print("[+] Testing: " + link)
                is_vuln_xss = self.test_xss_in_link(link)
                if is_vuln_xss:
                    print("[****] XSS discovered in " + link)

    # Test xss vulnerabilities in forms by submitting a script and checking to see if it appears in response
    def test_xss_in_form(self, form, url):
        xss_test_script = "<script>alert('test')</script>"
        response = self.submit_form(form,xss_test_script, url)
        return xss_test_script in response.content
            
    # Test xss vulnerabilities in links 
    def test_xss_in_link(self, url):
        xss_test_script = "<script>alert('test')</script>"
        url = url.replace("=","=" + xss_test_script)
        response = self.session.get(url)
        return xss_test_script in response.content
