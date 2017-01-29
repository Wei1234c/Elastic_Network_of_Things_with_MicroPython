# coding: utf-8

import time
import socket
import commander
import config
import data_transceiver
    

class Socket_client(commander.Commander):
    # Object control
    # @profile(precision=4)
    def __init__(self, server_ip, server_port):
        super().__init__()
        self.socket = None
        self.data_transceiver = None
        self.server_address = socket.getaddrinfo(server_ip, server_port)[-1][-1]        
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
        self.socket.close()
        

    # @profile(precision=4)
    def stopped(self):
        return self.status['Stop']
        
        
    
    # Socket operations
    # @profile(precision=4)
    def connect(self):        
        while True: 
            if self.stopped(): break             
                
            try:
                self.status['Datatransceiver ready'] = False
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_transceiver = data_transceiver.Data_transceiver()
                self.status['Datatransceiver ready'] = True
                self.message = None
                self.status['Is connected'] = False
                self.socket.connect(self.server_address)
                self.on_connected()  
                
            except Exception as e:
                print(e)
                time.sleep(config.CLIENT_RETRY_TO_CONNECT_AFTER_SECONDS)
            
    
    # @profile(precision=4)
    def on_connected(self):
        print('\n[connected: {0}]'.format(self.server_address))
        self.status['Is connected'] = True
        self.receive()


    # @profile(precision=4)
    def on_closed(self):
        print('[closed: {}]'.format(self.server_address))
        del self.socket
            
    
    # @profile(precision=4)
    def receive(self):
        print('[Listen to messages]')
        self.socket.settimeout(config.CLIENT_RECEIVE_TIME_OUT_SECONDS)
        
        while True:
            if self.stopped(): break                 
            self.receive_one_cycle()

    
    # @profile(precision=4)
    def receive_one_cycle(self):
        try: 
            data = None
            data = self.socket.recv(config.BUFFER_SIZE)
            if len(data) == 0:  # If Broker shut down, need this line to close socket
                self.on_closed()
                # break
            self.on_receive(data)
            
        except Exception as e:                
            # Connection reset.
            if config.IS_MICROPYTHON:
                if str(e) == config.MICROPYTHON_SOCKET_CONNECTION_RESET_ERROR_MESSAGE:
                    raise e
            elif isinstance(e, ConnectionResetError):
                raise e
                
            # Receiving process timeout.
            self.process_messages()
        

    # @profile(precision=4)
    def on_receive(self, data):
        if data:
            data, message_string = self.data_transceiver.unpack(data)
            self.message = self.decode_message(message_string)
            print('\nData received: {0} bytes\nMessage:\n{1}\n'.format(len(data), self.get_OrderedDict(self.message)))
            