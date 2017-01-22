# coding: utf-8

import os
import sys
import time
import threading
 
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'node')))

import node


class Client(threading.Thread):
    
    def __init__(self):        
        super().__init__(name = 'Client')
        self.node = None
        self.ready = threading.Event()
        
        
    def __del__(self):
        self.stop()  
        
        
    def _request(self, node, receiver, message):
        message['receiver'] = receiver
        self.node.request(**message)
        
        
    def request(self, receiver, message):
        self._request(self.node, receiver, message)  
        
        
    def run(self):
        self.node = node.Node()
        self.ready.set()
        self.node.run()
       
       
    def stop(self):
        self.node.stop()