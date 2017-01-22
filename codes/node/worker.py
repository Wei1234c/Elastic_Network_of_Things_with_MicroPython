# coding: utf-8


import gc
import config
import socket_client
import worker_config


class Worker(socket_client.Socket_client): 
        
    # Object control
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        self.name = worker_config.WORKER_NAME
        print('My name is', self.name)
        self.message_queue_in = []
        self.message_queue_out = []
        # self.message_queue_result = []
        
         
    # Socket operations    
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
        self.send_message(message)
        self.status['Is connected'] = True
        self.receive()


    def on_receive(self, data):        
        super().on_receive(data)        
        self.message_queue_in.append(self.message)        
        self.process_messages()
                

    def process_messages(self):
        if config.IS_MICROPYTHON: print('[Memory - free: {}   allocated: {}]'.format(gc.mem_free(), gc.mem_alloc()))
        gc.collect()
        time_stamp = str(self.now())
        
        # outgoing messages requested by client
        if len(self.message_queue_out) > 0:
            self.send_message(message = self.message_queue_out.pop(0))        
        
        # incoming messages
        if len(self.message_queue_in) > 0:
            message = self.message_queue_in.pop(0) 
            
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

        
    def request(self, message):
        if self.status['Is connected']:
            time_stamp = str(self.now())
            message['message_id'] = time_stamp
            message['sender'] = self.name
            message['reply_to'] = self.name          
            message['result'] = None
            message['correlation_id'] = time_stamp
            self.message_queue_out.append(self.format_message(**message))        
            if self.status['Datatransceiver ready']: self.process_messages()
        else:
            raise Exception('Not connected yet.')
        

    def send_message(self, message):
        message_string = self.encode_message(**message)
        message_bytes = self.data_transceiver.pack(message_string)
        print('Sending {0} bytes\nMessage:\n{1}\n'.format(len(message_bytes), self.get_OrderedDict(message)))
        self.socket.sendall(message_bytes)