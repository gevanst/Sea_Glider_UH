from config import *
from hardware.gpio import GPIOControl
import time

gpio = GPIOControl()

def reset_bno(rst_pin):
    print("Resetting BNO055...")
    gpio.set_value(rst_pin, 0)
    time.sleep(0.1)
    gpio.set_value(rst_pin,1)
    time.sleep(0.1)
    gpio.set_value(rst_pin,0)
    time.sleep(0.1)
    


