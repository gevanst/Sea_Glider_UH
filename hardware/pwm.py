# module defining functions for enabling and setting PWM characteristics on the BBAI64
from config import *
import os

class PWMController:
    def __init__(self, pwm_chip_base, period_ns):
        self.pwm_chip_base = pwm_chip_base
        self.period_ns = period_ns
        self.path_b = f"{pwm_chip_base}pwm1"
        self.path_a = f"{pwm_chip_base}pwm0"
        
        # Set the period for both channels
        # both channels on same pwm driver must have the same period since they use same clock signal
        self.set_pwm_period(self.path_a, period_ns)
        self.set_pwm_period(self.path_b, period_ns)
        self.set_pwm_dc(self.path_a, 0)
        self.set_pwm_dc(self.path_b, 0)
        print("duty cycle is 0")
        # Enable both PWM channels initially
        #self.enable_channel(self.path_a, enable = True)
        #self.enable_channel(self.path_b, enable = True)
        
        #self.enable_channel(self.path_a, enable = False) #
        #self.enable_channel(self.path_b, enable = False) #
        
        #self.enable_channel(self.path_a, enable = True)
        #self.enable_channel(self.path_b, enable = True)
        #print("both channels enabled")
        # Set initial duty cycle to 0


    # function to enable or disable a PWM channel by setting the enable file in the channel directory to 1 or 0
    def enable_channel(self, path, enable):
        enable_path = os.path.join(path, "enable")
        try:
            with open(enable_path, 'w') as enbl_file:
                enbl_file.write("1" if enable else "0")
        except IOError as e:
            print(f"Failed to {'enable' if enable else 'disable'} PWM at {enable_path}: {e}")

    # function to set the period of a PWM channel by writing the desired period in nanoseconds to the period file in the channel directory
    def set_pwm_period(self, path, period_ns):
        period_path = f"{path}/period"
        try:
            with open(period_path, 'w') as period_file:
                period_file.write(str(period_ns))
                print("period set")
        except IOError as e:
            print(f"Failed to set PWM period: {e}")

    # function to set the duty cycle of a PWM channel by writing the desired duty cycle in nanoseconds to the duty_cycle file in the channel directory
    def set_pwm_dc(self, full_path, dc_percent):
        dc_path = f"{full_path}/duty_cycle"
        
        #make sure channel is enabled
        self.enable_channel(full_path, enable = True)
        
        if dc_percent <= 5:
            # Disable the channel
            dc_ns = 0
            print("dc is set to zero")
        elif dc_percent >= 90:
            dc_ns = PWM_DC_MAX_NS
            print("dc is set to max")
        else:
            dc_ns = int((dc_percent / 90) * 900000)
            print("dc set to something in between")
        
        try:
            with open(dc_path, 'w') as dc_file:
                dc_file.write(str(dc_ns))
                print("duty cycle set")
        except IOError as e:
            print(f"Failed to set PWM duty cycle: {e}")