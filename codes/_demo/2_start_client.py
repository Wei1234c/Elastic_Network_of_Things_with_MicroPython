# coding: utf-8

import os
import sys
 
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'client')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'node')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'micropython')))
 
import client
from collections import OrderedDict
 

def main():
    
    try:
        # start and wait until client thread is ready
        the_client = client.Client()
        the_client.daemon = True
        the_client.start()
        the_client.ready.wait() 
        
        
        # nodes ************** need to modify accordingly.
        # check out Broker's console for the list of nodes.
        remote_nodes = ['NodeMCU_1dsc000', 'NodeMCU_f1d30800']                     
        # remote_nodes = ['NodeMCU_1dsc000']                     
        
        
        # messages
        messages = OrderedDict()
        
        messages['blink_led'] = {'type': 'command',
                                 'command': 'blink led',
                                 'kwargs': {'times': 10, 'forever': False, 'on_seconds': 0.1, 'off_seconds': 0.1}}

        messages['read_GPIOs'] = {'type': 'command',
                                  'command': 'read GPIOs',
                                  'need_result': True}                                      
        
        # messages['write_GPIOs'] = {'type': 'command',
                                   # 'command': 'write GPIOs',
                                   # 'kwargs': {'pins_and_values': [(2, 0), (2, 1), (2, 0),]}} 

        # messages['test eval'] = {'type': 'eval',
                                 # 'to_evaluate': '2+3',
                                 # 'need_result': True}                                   

        # messages['test exec'] = {'type': 'exec',
                                 # 'to_exec': 'print("Testing exec !")'}
        
        # with open('script_to_deploy.py') as f:
            # script = f.read()        
        # messages['test upload script'] = {'type': 'script', 
                                          # 'script': script}                                        
        
        # send out the messages
        for remote_node in remote_nodes:
            for message in messages.values():
                the_client.request(remote_node, message)
                
        # stop()
        the_client.join()
        print ('Demo stopped _______________________________')
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        sys.exit(1)            
                
        
if __name__ == '__main__':
    main()
