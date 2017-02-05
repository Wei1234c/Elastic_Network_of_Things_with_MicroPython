# coding: utf-8


# noinspection PyPep8
class Message_client():
    # Object control
    # @profile(precision=4)
    def __init__(self, server_ip, server_port):
        self.parent = None
        self.message = None
        self.server_address = None
        self.status = {'Datatransceiver ready': False, 
                       'Is connected': False,
                       'Stop': False}
 

    # @profile(precision=4)
    def __del__(self):
        self.parent = None
        
 
    # @profile(precision=4)
    def set_parent(self, parent = None):        
        self.parent = parent

                  
    # @profile(precision=4)
    def run(self):        
        self.connect()
 
 
    # @profile(precision=4)
    def stop(self):
        self.status['Stop'] = True
        self.close()
        

    # @profile(precision=4)
    def stopped(self):
        return self.status['Stop']
        
        
    
    # @profile(precision=4)
    def connect(self):        
        pass

        
    # @profile(precision=4)
    def on_connect(self):
        print('\n[Connected: {0}]'.format(self.server_address))
        self.status['Is connected'] = True
        self.receive()
        
        
    # @profile(precision=4)
    def close(self):
        self.on_closed()
        

    # @profile(precision=4)
    def on_closed(self):
        print('[Closed: {}]'.format(self.server_address))
            
    
    # @profile(precision=4)
    def receive(self):
        print('[Listen to messages]')

    
    # @profile(precision=4)
    def receive_one_cycle(self):
        pass
        

    # @profile(precision=4)
    def on_receive(self, data):
        if data:
            print('\nData received: {0} bytes'.format(len(data)))
            
            
    # @profile(precision=4)
    def process_messages(self):  
        pass
        

    # @profile(precision=4)
    def send_message(self, message_string):  
        print('\nSending {} bytes'.format(len(message_string)))