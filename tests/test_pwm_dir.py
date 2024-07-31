from config import *
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
import time
import unittest

# Initialize PWM controller for m4 motor cape
pwm = PWMController(PWM_CHIP_BASE, PWM_PERIOD_NS)
gpio = GPIOControl()

gpio.setup_pin(351, direction='out', default_value=0)

gpio.set_value(351, 1)
pwm.set_pwm_dc(M4_PATH, 50)
time.sleep(0.5)

pwm.set_pwm_dc(M4_PATH, 0)
gpio.cleanup(351)