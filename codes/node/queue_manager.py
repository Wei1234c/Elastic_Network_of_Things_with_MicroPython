# coding: utf-8

import time
import config
import asynch_result
       

class Queue_manager():
    
    # @profile(precision=4)
    def __init__(self):
        self._message_queue_in = []
        self._message_queue_out = []
        self._requests_need_result = {}
        self.lastest_request_time = 0

        
    # @profile(precision=4)
    def whether_requests_time_out(self):
        now = time.time()
        if now - self.lastest_request_time > config.REQUESTS_NEED_RESULT_TIME_TO_LIVE:
            self._requests_need_result = {}                
        self.lastest_request_time = now
        
        
    # @profile(precision=4)
    def append_request_message(self, message):
        self._message_queue_out.append(message)
        if message.get('need_result'):  # need result, wait for reply.
            self.whether_requests_time_out()
            self._requests_need_result[message.get('correlation_id')] = {'message_id': message.get('message_id')}            
            return asynch_result.Asynch_result(message.get('correlation_id'), self._requests_need_result)

        
    # @profile(precision=4)
    def append_received_message(self, message):
        self._message_queue_in.append(message)
        if message.get('type') == 'result':
            correlation_id = message.get('correlation_id')
            request = self._requests_need_result.get(correlation_id)
            if request:                 
                request['result'] = message.get('result')
                request['is_replied'] = True
        
        
    # @profile(precision=4)
    def pop_request_message(self):
        return self._message_queue_out.pop(0) if len(self._message_queue_out) > 0 else None        

        
    # @profile(precision=4)
    def pop_received_message(self):
        return self._message_queue_in.pop(0) if len(self._message_queue_in) > 0 else None