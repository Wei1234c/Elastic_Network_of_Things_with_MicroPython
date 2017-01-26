# coding: utf-8


import gc
import config
import socket_client
import queue_manager
import worker_config


class Worker(socket_client.Socket_client, queue_manager.Queue_manager): 
        
    # Object control
    # @profile(precision=4)
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        queue_manager.Queue_manager.__init__(self)
        self.name = worker_config.WORKER_NAME
        print('My name is', self.name)
        
         
    # Socket operations 
    # @profile(precision=4)
    def on_connected(self):
        # set my name
        message = self.format_message(sender = self.name,
                                      receiver = config.SERVER_NAME,                                       
                                      info = '*** Hello! My name is {0} ***'.format(self.name),
                                      type = 'command', 
                                      command = 'set connection name',
                                      kwargs = {'name': self.name}, 
                                      need_result = True)
                                      
        print('\n[connected: {0}]'.format(self.server_address))
        self.request(message)              
        self.status['Is connected'] = True
        self.receive()


    # @profile(precision=4)
    def on_receive(self, data):        
        super().on_receive(data)        
        self.append_received_message(self.message)
        self.process_messages()
        
        
    # @profile(precision=4)
    def process_messages(self):
        if config.IS_MICROPYTHON:
            print('[Memory - free: {}   allocated: {}]'.format(gc.mem_free(), gc.mem_alloc()))
        gc.collect()
        time_stamp = str(self.now())
        
        # outgoing requested messages
        message = self.pop_request_message()
        if message: self.send_message(message = message)        
        
        # incoming messages
        message = self.pop_received_message()
        if message: 
            
            # got result from somewhere else, no need to reply.
            if message.get('type') == 'result':
                pass
                
            else:
                # do whatever said in the message.   
                message, message_string = self.do(message)
                
                try:
                    if message:
                        reply_message = self.format_message(message_id = time_stamp,
                                                            sender = self.name,
                                                            receiver = message.get('sender'),
                                                            type = 'result',
                                                            need_result = False, result = message.get('result'),
                                                            reply_to = self.name,
                                                            correlation_id = message.get('correlation_id'))
                        
                        print('\nProcessed result:\n{0}\n'.format(self.get_OrderedDict(reply_message)))
                        
                        if message.get('need_result'):      
                            self.send_message(reply_message)
                    
                except Exception as e:
                    print(e, 'No result to return.')

        
    # @profile(precision=4)
    def request(self, message):
        time_stamp = str(self.now())
        message['message_id'] = time_stamp
        message['sender'] = self.name
        message['reply_to'] = self.name          
        message['result'] = None
        message['correlation_id'] = time_stamp
        asynch_result = self.append_request_message(self.format_message(**message))        
        if self.status['Datatransceiver ready']: self.process_messages()
        return message, asynch_result
        

    # @profile(precision=4)
    def send_message(self, message):
        message_string = self.encode_message(**message)
        message_bytes = self.data_transceiver.pack(message_string)
        print('Sending {0} bytes\nMessage:\n{1}\n'.format(len(message_bytes), self.get_OrderedDict(message)))
        self.socket.sendall(message_bytes)