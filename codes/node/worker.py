# coding: utf-8

import os
import sys   
import time
import gc
from config import *
from socket_client import Socket_client 
from node_config import *


if IS_MICROPYTHON:
    from hardware import *
    from led import *
    from u_python import *
    from watchdog import *    
    now = time.ticks_ms
    import machine
else:    
    import datetime
    now = datetime.datetime.now


class Worker(Socket_client): 
        
    # Object control
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        self.name = WORKER_NAME
        print('My name is ', self.name)
        self.message_queue_in = []
        self.message_queue_out = []
        # self.message_queue_result = []
        
         
    # Socket operations    
    def on_connected(self):
        # set my name
        message = self.format_message(sender = self.name,
                                      receiver = SERVER_NAME,                                       
                                      info = '*** Hello! My name is {0} ***'.format(self.name),
                                      type = 'command', 
                                      command = 'set connection name',
                                      kwargs = {'name': self.name}, 
                                      need_result = True)                                      
        self.send_message(message)
        super().on_connected()


    def on_receive(self, data):
        super().on_receive(data)      
        self.message_queue_in.append(self.message)        
        self.process_messages()
                

    def process_messages(self):
        time_stamp = str(now())
        
        # outgoing messages requested by client
        if len(self.message_queue_out) > 0:
            self.send_message(message = self.message_queue_out.pop(0))        
        
        # incoming messages
        if len(self.message_queue_in) > 0:
            message = self.message_queue_in.pop(0) 
            
            # got result from somewhere else, no need to reply.
            if message.get('type') == 'result':
                pass
                
            else:
                # do whatever said in the message.   
                message, message_string = self.do(message)
                
                try:
                    if message:
                        reply_message = self.format_message(message_id = time_stamp,
                                                            sender = self.name,
                                                            receiver = message.get('sender'),
                                                            type = 'result',
                                                            need_result = False, result = message.get('result'),
                                                            reply_to = self.name,
                                                            correlation_id = message.get('correlation_id'))
                        
                        print('\nProcessed result:\n{0}\n'.format(self.get_OrderedDict(reply_message)))
                        # return result
                        if message.get('need_result'):                    
                            self.send_message(reply_message)
                    
                except Exception as e:
                    print(e, 'No result to return.')

        
    def request(self, message):
        time_stamp = str(now())
        message['message_id'] = time_stamp
        message['sender'] = self.name
        message['reply_to'] = self.name          
        message['result'] = None
        message['correlation_id'] = time_stamp
        self.message_queue_out.append(self.format_message(**message))
        # self.process_messages()
        

    def send_message(self, message):
        message_string = self.encode_message(**message)
        message_bytes = self.data_transceiver.pack(message_string)
        print('Sending {0} bytes\nMessage:\n{1}\n'.format(len(message_bytes), self.get_OrderedDict(message)))
        self.socket.sendall(message_bytes)
        print('GC recycled: ', gc.collect())