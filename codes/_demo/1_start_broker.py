# coding: utf-8

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'broker')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))

from broker import *
 

def main():    
    try:
        the_broker = Broker()
        the_broker.run()        
        the_broker.hub.join()
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        sys.exit(1)  
        
if __name__ == '__main__':
    main()
