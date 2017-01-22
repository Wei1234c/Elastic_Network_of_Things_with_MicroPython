# coding: utf-8

from abc import ABCMeta, abstractmethod
import socket
import select
import threading
import datetime
import time
import config 
import connection_pool
import commander


class Socket_server(threading.Thread,
                    connection_pool.Connection_pool,
                    commander.Commander, 
                    metaclass = ABCMeta):

    # Object control
    def __init__(self, bind_ip, bind_port, max_concurrent_connections = 200):        
        super().__init__()
        self.name = config.SERVER_NAME
        connection_pool.Connection_pool.__init__(self)
        commander.Commander.__init__(self)
        self._stop = threading.Event()
        self._stop.clear()
        
        # Socket
        self.bind_address = socket.getaddrinfo(bind_ip, bind_port)[-1][-1]         
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)       
        self.socket.bind(self.bind_address)
        self.socket.listen(max_concurrent_connections)

        
    def __del__(self):
        self.parent = None
        del self.parent
        
        
    def set_parent(self, parent):        
        self.parent = parent
       
                  
    def run(self):        
        self.listen()
 

    def stop(self):
        print('Server set to stop __________________________')
        self._stop.set()
            

    def stopped(self):
        return self._stop.is_set()
     

        
    # Socker server operations
    def listen(self):
        
        threading.Thread(target = self.probe_connections , 
                         name = 'Workers heart-beat probing',
                         daemon = True).start()   
        
        while True:
            if self.stopped(): break
                
            # generate list of sockets
            sockets = list(self.get_sockets_list())
            sockets.append(self.socket)
            
            # select
            list_to_read, _, _ = select.select(sockets, [], [], config.SERVER_POLLING_REQUEST_TIMEOUT_SECONDS)
            
            # process tasks
            for self.socket_being_read in list_to_read:
                # new connection
                if self.socket_being_read is self.socket:
                    self.on_accept()
                    # connections list has changed
                    # need to escape for loop to re-generate the new list of sockets
                    break
                    
                else:
                    # try to receive data 
                    try: 
                        data = self.socket_being_read.recv(config.BUFFER_SIZE)
                        if len(data) == 0:
                            # self.on_close()
                            ## connections list has changed
                            ## need to escape for loop to re-generate the new list of sockets
                            # break
                            pass
                        else:
                            self.received_data = data
                            self.on_receive()                            
                    except ConnectionResetError as e:
                        self.on_close()
                        print(e)                        

            
    def on_accept(self):
        # accept
        socket, address = self.socket.accept()
        # address = address[0]
        print('\n[{0} has connected]'.format(address))
        
        # register connection  
        connection = self.register_connection(address, socket)
        self.print_connections()
        return connection
        
    
    def on_receive(self):
        data = self.received_data
        data, message_string = self.data_transceivers[self.socket_being_read].unpack(data)
        message = self.decode_message(message_string) 
        print('\nData received: {0} bytes\nMessage:\n{1}\n'.format(len(data), self.get_JSONized_dict(message)))
        
        self.process_message(message)
        
        
    def on_close(self):
        peer = self.socket_being_read.getpeername()
        address = peer
        print ('\n[{0} has disconnected]\n'.format(address))
                
        self.remove_connection(address)         
        self.print_connections()
                
        
    def probe_connections(self):
        while True:
            if self.stopped(): break                
            print('Heart-beat probing at: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))            
            
            message = {'sender': self.name,
                       'receiver': 'all workers',
                       'type': 'info',
                       'info': 'Just check to see if you are still there. No reply needed.', 
                       'need_result': False}            
            
            for socket in self.get_sockets_list():
                message_string = self.encode_message(**message)
                message_bytes = self.data_transceivers[socket].pack(message_string)
                socket.sendall(message_bytes)
            
            time.sleep(config.HEART_BEAT_PROBING_PER_SECONDS)