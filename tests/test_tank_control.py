from config import *
from control.PD_controller import PDController
from hardware.adc import read_adc
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
import time
import logging
from datetime import datetime
from Adafruit_BNO055 import BNO055

bno = BNO055.BNO055(busnum=5)

def get_input_vec():
    while True:
        try:
            user_input = input("Enter desired pitch position and desired roll position, separated by a space (e.g., '1000 500'): ")
            vector = list(map(int, user_input.split()))
            
            if len(vector) == 2:
                print(vector)
                return vector
            else:
                print("Invalid input. Please enter exactly 2 integer values separated by a space.")
        except ValueError:
            print("Invalid input. Please enter integer values only.")

def get_run():
    while True:
        try:
            user_input = input("Enter y or n to run again: ")
            if user_input == "y":
                return True
            else:
                return False
        except ValueError:
            print("Invalid input")

def input_check(vector):
    if vector[0] < PITCH_POT_MIN or vector[0] > PITCH_POT_MAX:
        print("Desired pitch position out of range. Setting to minimum safety position.")
        vector[0] = PITCH_POT_MIN if vector[0] < PITCH_POT_MIN else PITCH_POT_MAX
    else:
        print("pitch is good")

    if vector[1] < ROLL_POT_MIN or vector[1] > ROLL_POT_MAX:
        print("Desired roll position out of range. Setting to minimum safety position.")
        vector[1] = ROLL_POT_MIN if vector[1] < ROLL_POT_MIN else ROLL_POT_MAX
    else:
        print("we're good")
    return vector

def move_to_pos(setpoint, motor_path, motor_dir, pot, controller):
    pos = read_adc(pot)
    while pos != setpoint:
        output = controller.compute(pos) #compute with input of current position
        if output < 0:
            gpio.set_value(motor_dir, 0)
            pwm.set_pwm_dc(motor_path, abs(output))
        elif output > 0:
            gpio.set_value(motor_dir, 1)
            pwm.set_pwm_dc(motor_path, abs(output))
        else:
            pwm.set_pwm_dc(motor_path, 0)
        pos = read_adc(pot)
        print(pos)

print("starting tank control test")
time.sleep(2)
print("1")
pwm = PWMController(PWM_CHIP_BASE, PWM_PERIOD_NS)
time.sleep(2)
print("2")
pwm.set_pwm_dc(M4_PATH, 0)
time.sleep(2)
print("3")
pwm.set_pwm_dc(M3_PATH, 0)
print("controller set and dcs are 0")
time.sleep(2)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'test_log_{timestamp}'

with open(filename, 'w') as log_file:
    log_file.write("date hourminuteseconds unix seconds, heading, roll, pitch\n")

logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt = '%Y-%m-%d %H%M%S'
)

pos_I_pitch = read_adc(PITCH_POT_PATH)  # Read initial position of pitch motor
pos_I_roll = read_adc(ROLL_POT_PATH)  # Read initial position of roll motor

gpio = GPIOControl()
print("gpio controller setup")
time.sleep(2)
gpio.setup_pin(M4_DIR_PIN, direction='out', default_value=0)  # Set up pitch motor direction pin M4
gpio.setup_pin(M3_DIR_PIN, direction='out', default_value=0)  # Set up roll motor direction pin M3


# Create PD controllers
kp, kd = 10, 2
pitch_controller = PDController(Kp=kp, Kd=kd, setpoint=pos_I_pitch)
roll_controller = PDController(Kp=kp, Kd=kd, setpoint=pos_I_roll)

run=True

try:
    while run:
        print("Current Positions:")
        print("Pitch raw: ")
        print(pos_I_pitch)
        print("roll raw: ")
        print(pos_I_roll)
        time.sleep(1)
        heading, roll, pitch = bno.read_euler()
        print("Heading: ", heading, "Roll: ", roll, "Pitch: ", pitch)
        current_time = time.time()
        logging.info(f"{current_time:0.3f}, {heading:0.2f}, {roll:0.2f}, {pitch:0.2f}")
        
        desired_pos = get_input_vec()
        desired_pos = input_check(desired_pos)
        
        # Move to desired pitch position
        pitch_controller.setpoint = desired_pos[0]
        move_to_pos(desired_pos[0], M4_PATH, M4_DIR_PIN, PITCH_POT_PATH, pitch_controller)
        pwm.set_pwm_dc(M4_PATH, 0)
        
        # Move to desired roll position
        roll_controller.setpoint = desired_pos[1]
        move_to_pos(desired_pos[1], M3_PATH, M3_DIR_PIN, ROLL_POT_PATH, roll_controller)
        pwm.set_pwm_dc(M3_PATH, 0)
        run = get_run()
        
        
        
finally:
    pwm.set_pwm_dc(M4_PATH, 0)
    pwm.set_pwm_dc(M3_PATH, 0)
    print("stopping motors and program")


