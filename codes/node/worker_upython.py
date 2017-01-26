# coding: utf-8


import time
import config
import worker 
import led
import u_python  


class Worker(worker.Worker): 
        
    # Object control
    # @profile(precision=4)
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        self.now = time.ticks_ms
        
        
    # code book_______________________
    # @profile(precision=4)
    def set_default_code_book(self):
        code_book = {'read GPIOs': self.read_GPIOs,
                     'write GPIOs': self.write_GPIOs,
                     'blink led': self.blink_led}      
        self.set_code_book(code_book)        
        
        
    # Specialized functions__________
    # @profile(precision=4)
    def read_GPIOs(self): 
        return u_python.read_GPIOs_pins() if config.IS_MICROPYTHON else "(Pin 16: 1, Pin 5: 0, Pin 13: 1, Pin 12: 1, Pin 14: 1, Pin 15: 0)"


    # @profile(precision=4)
    def write_GPIOs(self, pins_and_values = None): 
        return u_python.write_GPIOs_pins(pins_and_values) if config.IS_MICROPYTHON else "(Pin 16: 1, Pin 5: 0, Pin 13: 1, Pin 12: 1, Pin 14: 1, Pin 15: 0)"
                        
    
    # @profile(precision=4)
    def blink_led(self, times = 1, forever = False, on_seconds = 0.5, off_seconds = 0.5):
        if config.IS_MICROPYTHON:
            led.blink_on_board_led(times = times, 
                                   forever = forever,
                                   on_seconds = on_seconds,
                                   off_seconds = off_seconds)