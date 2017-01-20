# coding: utf-8

import os
import machine
from hardware import *
from led import *
from watchdog import *   



def get_output_pin(id, mode = machine.Pin.OUT, pull = None):
    return machine.Pin(id, mode, pull)
    
    
def get_input_pin(id, mode = machine.Pin.IN):
    return machine.Pin(id, mode)
    

# import u_python;u_python.del_all_files();import os;os.listdir()
def del_all_files():
    for file in os.listdir():
        os.remove(file)
    os.listdir()

        
def read_GPIOs_pins():
    status = sorted([(id, get_input_pin(id).value()) for id in list(gpio_pins[5:])])    
    print("GPIO pins status: \n{0}".format(status))
    return status

    
def read_GPIOs_pin(id):
    return id, get_input_pin(id).value()     

    
def write_GPIOs_pins(pins_and_values):
    for id, value in pins_and_values:
        the_pin = get_output_pin(id, mode = machine.Pin.OUT)
        the_pin.value(value)
    return read_GPIOs_pins()    