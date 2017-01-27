# coding: utf-8

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'broker')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))

import broker 
 

def main():    
    try:
        the_broker = broker.Broker()
        the_broker.run()
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        the_broker.stop()
        the_broker = None
        sys.exit(1)  
        
if __name__ == '__main__':
    main()
