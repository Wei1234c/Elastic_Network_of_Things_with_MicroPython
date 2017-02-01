# coding: utf-8

# noinspection PyUnresolvedReferences
import config


# noinspection PyMethodMayBeStatic
class Data_transceiver:
        
    # @profile(precision=4)
    def __init__(self):
        self.buffer = b''

    
    # @profile(precision=4)
    def pack(self, data):
        if data:
            return b'' + config.PACKAGE_START + data.encode() + config.PACKAGE_END
        
        
    # http://dabeaz.blogspot.tw/2010/01/few-useful-bytearray-tricks.html        
    # @profile(precision=4)
    def unpack(self, data):        
        if data:
            self.buffer += data
            end_at = self.buffer.find(config.PACKAGE_END)
            
            if end_at > -1:
                start_at = self.buffer.find(config.PACKAGE_START)
                message = self.buffer[start_at + len(config.PACKAGE_START): end_at]
                self.buffer = self.buffer[end_at + len(config.PACKAGE_END):]
                return data, message.decode()
                
        return data, None
