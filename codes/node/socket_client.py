# coding: utf-8

import time
import socket
# noinspection PyUnresolvedReferences
import config
# noinspection PyUnresolvedReferences
import message_client
# noinspection PyUnresolvedReferences
import data_transceiver


# noinspection PyPep8
class Message_client(message_client.Message_client):
    # Object control
    # @profile(precision=4)
    def __init__(self, server_ip, server_port):
        super().__init__(server_ip, server_port)
        self.server_address = socket.getaddrinfo(server_ip, server_port)[-1][-1]     
        self.socket = None
        self.data_transceiver = None   
    
    
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
                self.on_connect()  
                
            except Exception as e:
                print(e)
                time.sleep(config.CLIENT_RETRY_TO_CONNECT_AFTER_SECONDS)
      
        
    # @profile(precision=4)
    def close(self):
        self.socket.close()
        super().close()
        

    # @profile(precision=4)
    def on_closed(self):
        super().on_closed()
        del self.socket
            
    
    # @profile(precision=4)
    def receive(self):
        super().receive()
        
        self.socket.settimeout(config.CLIENT_RECEIVE_TIME_OUT_SECONDS)
        
        while True:
            if self.stopped(): break    
                
            try: 
                # noinspection PyUnusedLocal
                data = None
                data = self.socket.recv(config.BUFFER_SIZE)
                if len(data) == 0:  # If Broker shut down, need this line to close socket
                    self.on_closed()
                    break
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
    def receive_one_cycle(self):
        try: 
            # noinspection PyUnusedLocal
            data = None
            data = self.socket.recv(config.BUFFER_SIZE)
            if len(data) == 0:  # If Broker shut down, need this line to close socket
                self.on_closed()
            self.on_receive(data)
            
        except Exception as e:                
            pass
        

    # @profile(precision=4)
    def on_receive(self, data):
        super().on_receive(data)
        if data:
            data, message_string = self.data_transceiver.unpack(data)
            self.message = message_string
            

    # @profile(precision=4)
    def send_message(self, message_string):  
        super().send_message(message_string)
        message_bytes = self.data_transceiver.pack(message_string)   
        self.socket.sendall(message_bytes)            