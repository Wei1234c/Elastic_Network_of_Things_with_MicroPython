# coding: utf-8


import datetime
import worker


class Worker(worker.Worker): 
        
    # Object control
    # @profile(precision=4)
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        self.now = datetime.datetime.now
        
        
    # code book_______________________
    # @profile(precision=4)
    def set_default_code_book(self):
        code_book = {'read GPIOs': self.read_GPIOs,
                     'write GPIOs': self.write_GPIOs,
                     'blink led': self.blink_led}      
        self.set_code_book(code_book)        
        
        
    # Specialized functions__________
    def read_GPIOs(self, pins): 
        return 'Not applicable.'
        

    # @profile(precision=4)
    def write_GPIOs(self, pins_and_values):
        return 'Not applicable.'
        
    
    # @profile(precision=4)
    def blink_led(self, times = 1, forever = False, on_seconds = 0.5, off_seconds = 0.5):
        return 'Not applicable.'