# coding: utf-8

import os
import sys

IS_MICROPYTHON = sys.implementation.name == 'micropython'

if not IS_MICROPYTHON:
    sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))
        
from config import *

if IS_MICROPYTHON:
    from worker_upython import *
else:
    from worker_upython import *
    
from commander import *
    

class Node(Commander):

    def __init__(self):
        super().__init__()
        self.worker = Worker(BROKER_HOST, HUB_PORT)
        self.worker.set_parent(self)
        
        
    def __del__(self):
        self.stop()
        
        
    def set_default_code_book(self):
        code_book = {}
        self.set_code_book(code_book) 
        
            
    def run(self): 
        self.worker.run()
 
 
    def stop(self): 
        self.worker.stop()
        self.worker.set_parent(None)
        del self.worker
        
        
    def request(self, **message):
        self.worker.request(message)
        
        

def main():
    try:
        node = Node()
        node.run() 
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        sys.exit(1)            
                
        
if __name__ == '__main__':
    main()
        


