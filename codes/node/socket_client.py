# coding: utf-8

import time
import socket
import commander
import config
import data_transceiver
    

class Socket_client(commander.Commander):
    # Object control
    def __init__(self, server_ip, server_port):
        super().__init__()
        self.socket = None
        self.server_address = socket.getaddrinfo(server_ip, server_port)[-1][-1]
        self.data_transceiver_ready = False
        self.is_connected = False
        self._stop = False
 
    def __del__(self):
        self.parent = None
        
 
    def set_parent(self, parent = None):        
        self.parent = parent

                  
    def run(self):        
        self.connect()        
 
 
    def stop(self):
        self._stop = True
        

    def stopped(self):
        return self._stop
        
        
    
    # Socket operations
    def connect(self):        
        while True: 
            if self.stopped(): break             
                
            try:
                self.data_transceiver_ready = False
                self.is_connected = False
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_transceiver = data_transceiver.Data_transceiver()
                self.data_transceiver_ready = True
                self.message = None
                self.socket.connect(self.server_address)
                self.on_connected()  
                
            except Exception as e:
                print(e)
                time.sleep(config.CLIENT_RETRY_TO_CONNECT_AFTER_SECONDS)
            
    
    def on_connected(self):
        print('[connected: {0}]'.format(self.server_address))
        self.is_connected = True        
        self.receive()


    def on_closed(self):
        print('closed: ', self.server_address)
        del self.socket
            

    def receive(self):
        print('listen_to_command')
        self.socket.settimeout(config.CLIENT_RECEIVE_TIME_OUT_SECONDS)
        
        while True:
            if self.stopped(): break 
                
            data = None
            
            try: 
                data = self.socket.recv(config.BUFFER_SIZE)
                
                # connection closed
                if not data: 
                    self.on_closed()
                    break
                
                # receive data
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
 

    def on_receive(self, data):
        if data:
            # data received
            data, message_string = self.data_transceiver.unpack(data)
            self.message = self.decode_message(message_string)
            print('\nData received: {0} bytes\nMessage:\n{1}\n'.format(len(data), self.get_OrderedDict(self.message)))
            