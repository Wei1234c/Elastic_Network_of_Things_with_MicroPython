# coding: utf-8

import config

       
class Data_transceiver():
        
    # @profile(precision=4)
    def __init__(self):
        self.data = b''
        self.buffer = b''
        self.message = b''

    
    # @profile(precision=4)
    def pack(self, data):
        if data:
            return b'' + config.PACKAGE_START + data.encode() + config.PACKAGE_END
        
        
    # http://dabeaz.blogspot.tw/2010/01/few-useful-bytearray-tricks.html        
    # @profile(precision=4)
    def unpack(self, data):        
        if data:
            self.data = data
            self.buffer += self.data
            end_at = self.buffer.find(config.PACKAGE_END)
            
            if end_at > -1 :
                return self.extract_message()
                
        return data, None
        

    # @profile(precision=4)
    def extract_message(self):
        start_at = self.buffer.find(config.PACKAGE_START)
        end_at = self.buffer.find(config.PACKAGE_END)
        self.message = self.buffer[start_at + len(config.PACKAGE_START) : end_at]
        self.buffer = self.buffer[end_at + len(config.PACKAGE_END) : ]
        return self.data, self.message.decode()