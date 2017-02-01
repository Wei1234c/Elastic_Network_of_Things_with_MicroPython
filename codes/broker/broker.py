# coding: utf-8

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))

# noinspection PyPep8,PyUnresolvedReferences
import config
# noinspection PyPep8,PyUnresolvedReferences
import hub


class Broker:

    def __init__(self):
        super().__init__()
        self.hub = hub.Hub(config.BIND_IP, 
                           config.HUB_PORT, 
                           config.MAX_CONCURRENT_CONNECTIONS)
        self.hub.daemon = True
        
            
    def run(self):
        self.hub.start()
        

    def stop(self):
        self.hub.stop()
 
 
        
def main():        
    try:            
        broker = Broker()
        broker.run()
        broker.hub.join()
        print('Broker stopped. _____________________________')        
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        # noinspection PyUnboundLocalVariable
        broker.stop()
        # noinspection PyUnusedLocal
        broker = None
        sys.exit(1)
        

if __name__ == '__main__':
    main()
