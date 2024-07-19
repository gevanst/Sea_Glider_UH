import os
import sys
import time
import termios
import tty
from hardware.adc import read_adc
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
from control.PD_controller import PDController

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def manual_control():
    Kp, Kd = 1.0, 0.1  # PD controller gains
    pitch_setpoint = 0  # Initial setpoint for pitch
    roll_setpoint = 0   # Initial setpoint for roll
    pitch_controller = PDController(Kp, Kd, pitch_setpoint)
    roll_controller = PDController(Kp, Kd, roll_setpoint)

    gpio = GPIOControl()
    imu_reset_pin = 123  # Replace with the actual GPIO pin number for IMU reset
    gpio.setup_pin(imu_reset_pin, direction='out', default_value=0)

    print("Use arrow keys to adjust pitch and roll. Press 'q' to exit. Press 'r' to reset IMU.")

    try:
        while True:
            key = get_key()
            if key == 'q':
                break
            elif key == 'r':
                # Reset the IMU
                gpio.set_value(imu_reset_pin, 1)
                time.sleep(0.1)
                gpio.set_value(imu_reset_pin, 0)
                print("IMU reset.")
            elif key == '\x1b':  # Arrow keys start with an escape character
                key += sys.stdin.read(2)
                if key == '\x1b[A':  # Up arrow
                    pitch_setpoint += 50
                elif key == '\x1b[B':  # Down arrow
                    pitch_setpoint -= 50
                elif key == '\x1b[C':  # Right arrow
                    roll_setpoint += 50
                elif key == '\x1b[D':  # Left arrow
                    roll_setpoint -= 50

            # Read current ADC values
            current_pitch_adc = read_adc(pitch_adc_path)
            current_roll_adc = read_adc(roll_adc_path)

            # Compute control outputs using PD controllers
            pitch_output = pitch_controller.compute(current_pitch_adc)
            roll_output = roll_controller.compute(current_roll_adc)

            # Update PWM duty cycles based on PD controller outputs
            pwm.set_pwm_dc(pwm.path_a, pitch_output)
            pwm.set_pwm_dc(pwm.path_b, roll_output)

            time.sleep(0.1)  # Add a small delay to avoid busy looping

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    manual_control()