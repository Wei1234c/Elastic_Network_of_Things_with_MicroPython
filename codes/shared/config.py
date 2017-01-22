# coding: utf-8

import sys

# 'esp8266' or 'win32'
SYS_PLATFORM = sys.platform

# 'micropython' or 'cpython'
SYS_IMPLEMENTATION = sys.implementation.name
IS_MICROPYTHON = SYS_IMPLEMENTATION == 'micropython'
 

# import data_transceiver



## Must config ******************

# BROKER_HOST = '192.168.0.105'
BROKER_HOST = '192.168.0.105'
BIND_IP = '0.0.0.0'   # the ip which broker listens to.
HUB_PORT = 9662

## Must config ******************



DEBUG_MODE = True


# # print if in debug mode
# def dprint(*args, **kwargs):
    # if DEBUG_MODE:
        # print(*args, **kwargs)
   
   
# # a mock object to turn keyword dict into attributes        
# class Mock():
    # def __init__(self, key_words_dict):
        # if key_words_dict:
            # for key, value in key_words_dict.items(): setattr(self, key, value)
        

# Usually no need to config these.
SERVER_NAME = 'Hub'        
BUFFER_SIZE = 4096
PACKAGE_START = b'---PACKAGE_START---'
PACKAGE_END = b'---PACKAGE_END---'
CLIENT_RETRY_TO_CONNECT_AFTER_SECONDS = 3
CLIENT_RECEIVE_TIME_OUT_SECONDS = 1
MAX_CONCURRENT_CONNECTIONS = 200
SERVER_POLLING_REQUEST_TIMEOUT_SECONDS = 60 
HEART_BEAT_PROBING_PER_SECONDS = 60    
MICROPYTHON_SOCKET_CONNECTION_RESET_ERROR_MESSAGE = '[Errno 104] ECONNRESET' 
MICROPYTHON_SOCKET_RECEIVE_TIME_OUT_ERROR_MESSAGE = 'timed out' 
