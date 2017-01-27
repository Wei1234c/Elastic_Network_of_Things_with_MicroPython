# coding: utf-8

import os
import sys
import time
 
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'client')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'node')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))
sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'micropython')))
 
import client
from collections import OrderedDict

 
# @profile(precision=4)
def main():
    
    try:
        # start and wait until client thread is ready
        the_client = client.Client()
        the_client.start()
        
        
        # messages _____________________________________________
        messages = OrderedDict()

        messages['read_GPIOs'] = {'type': 'command',
                                  'command': 'read GPIOs',
                                  'need_result': True}
                                  
        messages['blink_led'] = {'type': 'command',
                                 'command': 'blink led',
                                 'kwargs': {'times': 10, 'forever': False, 'on_seconds': 0.1, 'off_seconds': 0.1}}                                      
        
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

                                          
        while not the_client.status['Is connected']:            
            time.sleep(1)
            print('Node not ready yet.')                                          
                                          
        # nodes _________________________________________________
        # remote_nodes = [{'name': 'Living room main light', 'type': 'D1 mini', 'id': 'NodeMCU_1dsc000'},
                        # {'name': 'Coffee maker', 'type': 'NodeMCU v2', 'id': 'NodeMCU_f1d30800'},
                        # {'name': 'Front gate', 'type': 'NodeMCU v2', 'id': 'NodeMCU_d1e0a200'},] 

        message = {'type': 'command',
                   'command': 'list connections by name',
                   'need_result': True}            
            
        _, asynch_result = the_client.request('Hub', message) 
        remote_nodes = asynch_result.get().keys()
        print('\n[____________ Connected nodes ____________]\n')        
        print('\nConnected nodes:\n{}\n'.format(remote_nodes))                                          
        
        
        print('\n[______________ Sending messages ______________]\n')
                
        results = []
        
        ## send out the messages
        for message in messages.values():
            for remote_node in remote_nodes:
                if remote_node != the_client.node.worker.name:
                    formatted_message, asynch_result = the_client.request(remote_node, message) 
                    results.append((formatted_message, asynch_result))

        # collect and print results        
        print('\n[_________ Wait few seconds for reply _________]\n')
        for (message, result) in results:
            try:
                if message.get('need_result'):
                    print('\n[Result for request]:\n___Request___:\n{0}\n___Result____:\n{1}\n'.format(message, result.get() if result else None))
            except Exception as e:
                print('\n[{}]\nMessage:\n{}'.format(e, message))
                
                
        # Wait a while        
        time.sleep(7)
        
        # Stopping
        the_client.stop()
        the_client = None
        print('\n[________________ Demo stopped ________________]\n')
        
    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        the_client.stop()
        the_client = None
        sys.exit(1) 
                
        
if __name__ == '__main__':
    main()
