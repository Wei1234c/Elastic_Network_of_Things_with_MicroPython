# coding: utf-8

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))

from config import *
from hub import *


class Broker():

    def __init__(self):
        super().__init__()
        self.hub = Hub(BIND_IP, HUB_PORT, MAX_CONCURRENT_CONNECTIONS)
        self.hub.daemon = True
        
            
    def run(self):
        self.hub.start()
 
 
        
def main():        
    try:            
        broker = Broker()
        broker.run()
        broker.hub.join()
        print('Broker stopped. _____________________________')        
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
        

if __name__ == '__main__':
    main()
