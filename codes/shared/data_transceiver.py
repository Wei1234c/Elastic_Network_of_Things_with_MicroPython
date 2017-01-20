# coding: utf-8

from config import *

       
class Data_transceiver():
        
    def __init__(self):
        self.data = b''
        self.buffer = b''
        self.message = b''
        self.header = PACKAGE_START
        self.header_length = len(self.header)
        self.tail = PACKAGE_END
        self.tail_length = len(self.tail)

    
    def pack(self, data):
        if data:
            packed_bytes = b'' + self.header + data.encode() + self.tail
            return packed_bytes
        
        
    # http://dabeaz.blogspot.tw/2010/01/few-useful-bytearray-tricks.html        
    def unpack(self, data):        
        if data:
            self.data = data
            self.buffer += self.data
            start_at = self.buffer.find(self.header)
            end_at = self.buffer.find(self.tail)
            
            if end_at > -1 :
                return self.extract_message()
                
        return data, None
        

    def extract_message(self):
        start_at = self.buffer.find(self.header)
        end_at = self.buffer.find(self.tail)
        # print('Receiving data:')
        # print('Buffer before extraction: {0} bytes\n{1}'.format(len(self.buffer), self.buffer))
        self.message = self.buffer[start_at + self.header_length : end_at]
        self.buffer = self.buffer[end_at + self.tail_length : ]
        # print('Buffer after extraction: {0} bytes\n{1}\n'.format(len(self.buffer), self.buffer))
        return self.data, self.message.decode()