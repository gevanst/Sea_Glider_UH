import sys
import time
import termios
import tty
from hardware.adc import read_adc
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
from control.PD_controller import PDController
from config import *

def get_key():
    fd = sys.stdin.fileno()  # Get the file descriptor for standard input
    old_settings = termios.tcgetattr(fd)  # Save the current terminal settings
    try:
        tty.setraw(fd)  # Set the terminal to raw mode for immediate character input
        ch = sys.stdin.read(1)  # Read a single character from standard input
    except Exception as e:
        print(f"Exception in get_key: {e}")
        ch = None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore the original terminal settings
    return ch  # Return the character read

def manual_control():
    Kp, Kd = 1.0, 0.1  # PD controller gains
    pitch_pos = read_adc(PITCH_POT_PATH)
    roll_pos = read_adc(ROLL_POT_PATH)
    pitch_controller = PDController(Kp, Kd, pitch_pos)
    roll_controller = PDController(Kp, Kd, roll_pos)

    pwm = PWMController(PWM_CHIP_BASE, PWM_PERIOD_NS)

    gpio = GPIOControl()
    gpio.setup_pin(351, direction='out', default_value=0)
    gpio.setup_pin(375, direction='out', default_value=0)

    print("Use arrow keys to adjust pitch and roll. Press 'q' to exit. Press 'r' to reset IMU.")

    try:
        while True:
            print("Waiting for key press...")  # Debug statement
            key = get_key()
            print(f"Key pressed: {key}")  # Debug statement
            
            if key is None:
                continue

            if key == 'q':
                break

            elif key == '\x1b':  # Arrow keys start with an escape character
                key += sys.stdin.read(2)
                print(f"Arrow key sequence: {key}")  # Debug statement
                if key == '\x1b[A':  # Up arrow
                    pitch_pos += 50
                elif key == '\x1b[B':  # Down arrow
                    pitch_pos -= 50
                elif key == '\x1b[C':  # Right arrow
                    roll_pos += 50
                elif key == '\x1b[D':  # Left arrow
                    roll_pos -= 50

            # Read current ADC values
            current_pitch_adc = read_adc(PITCH_POT_PATH)
            current_roll_adc = read_adc(ROLL_POT_PATH)

            # Compute control outputs using PD controllers
            pitch_output = pitch_controller.compute(current_pitch_adc)
            roll_output = roll_controller.compute(current_roll_adc)

            # Update PWM duty cycles and motor direction based on PD controller outputs
            if pitch_output < 0:
                gpio.set_value(M4_DIR_PIN, 0)
            elif pitch_output > 0:
                gpio.set_value(M4_DIR_PIN, 1)
            pwm.set_pwm_dc(M4_PATH, abs(pitch_output))

            if roll_output < 0:
                gpio.set_value(M3_DIR_PIN, 0)
            elif roll_output > 0:
                gpio.set_value(M3_DIR_PIN, 1)
            pwm.set_pwm_dc(M3_PATH, abs(roll_output))

            time.sleep(0.1)  # Small time buffer

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    manual_control()
