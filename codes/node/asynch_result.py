# coding: utf-8

import time
import config


class Asynch_result(): 
        
    # @profile(precision=4)
    def __init__(self, correlation_id, requests):
        self.correlation_id = correlation_id
        self._requests_need_result = requests
        self.request = self._requests_need_result.get(correlation_id)

        
    # @profile(precision=4)
    def remove_request(self): 
        self.request = None
        self._requests_need_result.pop(self.correlation_id)
        
    
    # @profile(precision=4)
    def get(self, timeout = config.ASYNCH_RESULT_TIMEOUT):
        start_time = time.time()
        
        if self.request:
            while True:
                if self.request.get('is_replied'):
                    result = self.request.get('result')
                    self.remove_request()
                    return result
                else:
                    time.sleep(config.ASYNCH_RESULT_RETRY_DELAY)
                    if time.time() - start_time > timeout:  # timeout
                        message_id = self.request.get('message_id')
                        self.remove_request()
                        raise Exception('Timeout: no result returned for request with message_id {}'.format(message_id))
        else:
            raise Exception('No such request for request with correlation_id {}'.format(self.correlation_id))