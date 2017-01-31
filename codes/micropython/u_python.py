# coding: utf-8

import machine
import hardware
    

# @profile(precision=4)
def get_output_pin(id, mode = machine.Pin.OUT, pull = None):
    return machine.Pin(id, mode, pull)
    
    
# @profile(precision=4)
def get_input_pin(id, mode = machine.Pin.IN):
    return machine.Pin(id, mode)


# @profile(precision=4)
def read_GPIOs_pins(pins):
    status = sorted([(id, get_input_pin(id).value()) for id in pins])
    return status

    
# @profile(precision=4)
def write_GPIOs_pins(pins_and_values):
    for id, value in pins_and_values:
        the_pin = get_output_pin(id, mode = machine.Pin.OUT)
        the_pin.value(value)
    return read_GPIOs_pins()    