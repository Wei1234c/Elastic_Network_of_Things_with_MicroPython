# coding: utf-8

import time
import config


class Asynch_result(): 
        
    # @profile(precision=4)
    def __init__(self, correlation_id, requests, yield_to):
        self.correlation_id = correlation_id
        self._requests_need_result = requests
        self.yield_to = yield_to
        
        
    # @profile(precision=4)    
    def get(self, timeout = config.ASYNCH_RESULT_TIMEOUT):
        start_time = time.time()
        request = self._requests_need_result.get(self.correlation_id)
        
        if request:
            while True:
                if request.get('is_replied'):
                    result = request.get('result')
                    # self._requests_need_result.pop(self.correlation_id)
                    return result
                else:
                    if time.time() - start_time > timeout:  # timeout
                        # self._requests_need_result.pop(self.correlation_id)
                        raise Exception('Timeout: no result returned for request with correlation_id {}'.format(self.correlation_id))
                    else:
                        pass
                        # self.yield_to()
        else:
            raise Exception('No such request for request with correlation_id {}'.format(self.correlation_id)) 
