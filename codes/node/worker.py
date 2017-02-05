# coding: utf-8


import gc
# noinspection PyUnresolvedReferences
import config
# noinspection PyUnresolvedReferences
import socket_client as message_client
# noinspection PyUnresolvedReferences
import commander
# noinspection PyUnresolvedReferences
import queue_manager
# noinspection PyUnresolvedReferences
import asynch_result
# noinspection PyUnresolvedReferences
import worker_config


class Worker(message_client.Message_client, queue_manager.Queue_manager, commander.Commander): 
        
    # Object control
    # @profile(precision=4)
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        queue_manager.Queue_manager.__init__(self)        
        commander.Commander.__init__(self)
        self.name = worker_config.WORKER_NAME
        print('My name is', self.name)
        
         
    # Socket operations 
    # @profile(precision=4)
    def on_connected(self):
        print('\n[Connected: {0}]'.format(self.server_address))
        
        # set my name
        self.set_connection_name()
        
        self.status['Is connected'] = True
        self.receive()
        

    # @profile(precision=4)
    def rename(self, name):
        self.name = name
        self.set_connection_name()
        
        
    # @profile(precision=4)
    def set_connection_name(self):
        # set my name
        message = self.format_message(sender = self.name,
                                      receiver = config.SERVER_NAME,
                                      message_type = 'command', 
                                      command = 'set connection name',
                                      kwargs = {'name': self.name}, 
                                      need_result = True)
        self.request(message)
        

    # @profile(precision=4)
    def on_receive(self, data):        
        super().on_receive(data)
        self.message = self.decode_message(self.message)
        print('Message:\n{}\n'.format(self.get_OrderedDict(self.message)))
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
            if message.get('message_type') == 'result':
                pass
                
            else:
                # do whatever said in the message.   
                message, message_string = self.do(message)
                
                try:
                    if message:
                        reply_message = self.format_message(message_id = time_stamp,
                                                            sender = self.name,
                                                            receiver = message.get('sender'),
                                                            message_type = 'result',
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
        message = self.format_message(**message)
        self.append_request_message(message)
        if self.status['Datatransceiver ready']: self.process_messages()
            
        async_result = None
        if message.get('need_result'):
            async_result = asynch_result.Asynch_result(message.get('correlation_id'),
                                                       self._requests_need_result,
                                                       self.receive_one_cycle)        
        return message, async_result
       

    # @profile(precision=4)
    def send_message(self, message):
        message_string = self.encode_message(**message)
        super().send_message(message_string)        
        print('Message:\n{}\n'.format(self.get_OrderedDict(message)))
        
