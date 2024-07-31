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

def move_to_pos(setpoint1, setpoint2, motor_path1, motor_path2, motor_dir1, motor_dir2, pot1, pot2, controller1, controller2):
    pos1 = read_adc(pot1)
    pos2 = read_adc(pot2)
    
    while pos1 != setpoint1:
        
        heading, roll, pitch = bno.read_euler()
        current_time = time.time()
        logging.info(f"{current_time:0.3f}, {heading:0.2f}, {roll:0.2f}, {pitch:0.2f}, {pos1:0.2f}, {pos2:0.2f}, {setpoint1:0.2f}, {setpoint2:0.2f}")
        
        output1 = controller1.compute(pos1) #compute with input of current position
        if output1 < 0:
            gpio.set_value(motor_dir1, 0)
            pwm.set_pwm_dc(motor_path1, abs(output1))
        elif output1 > 0:
            gpio.set_value(motor_dir1, 1)
            pwm.set_pwm_dc(motor_path1, abs(output1))
        else:
            pwm.set_pwm_dc(motor_path1, 0)
        pos1 = read_adc(pot1)
    
    pos1 = read_adc(pot1)
    pos2 = read_adc(pot2)
        
    while pos2 != setpoint2:
        
        heading, roll, pitch = bno.read_euler()
        current_time = time.time()
        logging.info(f"{current_time:0.3f}, {heading:0.2f}, {roll:0.2f}, {pitch:0.2f}, {pos1:0.2f}, {pos2:0.2f}, {setpoint1:0.2f}, {setpoint2:0.2f}")
        
        output2 = controller2.compute(pos2) #compute with input of current position
        if output2 < 0:
            gpio.set_value(motor_dir2, 0)
            pwm.set_pwm_dc(motor_path2, abs(output2))
        elif output2 > 0:
            gpio.set_value(motor_dir2, 1)
            pwm.set_pwm_dc(motor_path2, abs(output2))
        else:
            pwm.set_pwm_dc(motor_path2, 0)
        pos2 = read_adc(pot2)


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
    log_file.write("unix_seconds,heading,roll,pitch,current_pitch_pos,current_roll_pos,pitch_set_point,roll_set_point\n")

logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='%(message)s',
)

pos_I_pitch = read_adc(PITCH_POT_PATH)  # Read initial position of pitch motor
pos_I_roll = read_adc(ROLL_POT_PATH)  # Read initial position of roll motor

gpio = GPIOControl()
print("gpio controller setup")
time.sleep(2)
gpio.setup_pin(M4_DIR_PIN, direction='out', default_value=0)  # Set up pitch motor direction pin M4
gpio.setup_pin(M3_DIR_PIN, direction='out', default_value=0)  # Set up roll motor direction pin M3
print("motor direction pins setup")

# Create PD controllers
kp, kd = 10, 2
pitch_controller = PDController(Kp=kp, Kd=kd, setpoint=pos_I_pitch)
roll_controller = PDController(Kp=kp, Kd=kd, setpoint=pos_I_roll)

run=True

try:
    while run:
        pos_roll = read_adc(ROLL_POT_PATH)
        pos_pitch = read_adc(PITCH_POT_PATH)
        print("Current Positions:")
        print("Pitch raw: ")
        print(pos_pitch)
        print("roll raw: ")
        print(pos_roll)
        time.sleep(1)
        heading, roll, pitch = bno.read_euler()
        print("Heading: ", heading, "Roll: ", roll, "Pitch: ", pitch)
        current_time = time.time()
        logging.info(f"{current_time:0.3f}, {heading:0.2f}, {roll:0.2f}, {pitch:0.2f}")
        
        #get desired positions from user and then check against limits
        desired_pos = get_input_vec()
        desired_pos = input_check(desired_pos)
        
        # Move to desired positions
        pitch_controller.setpoint = desired_pos[0]
        roll_controller.setpoint = desired_pos[1]
        move_to_pos(desired_pos[0], desired_pos[1], M4_PATH, M3_PATH, M4_DIR_PIN, M3_DIR_PIN, PITCH_POT_PATH, ROLL_POT_PATH, pitch_controller, roll_controller)
        pwm.set_pwm_dc(M4_PATH, 0)
        pwm.set_pwm_dc(M3_PATH, 0)
        
        #ask for another input or exit program
        run = get_run()
        #read log values one more time before exiting program
        pos_roll = read_adc(ROLL_POT_PATH)
        pos_pitch = read_adc(PITCH_POT_PATH)
        roll_d = desired_pos[1]
        pitch_d = desired_pos[0]
        heading, roll, pitch = bno.read_euler()
        current_time = time.time()
        logging.info(f"{current_time:0.3f}, {heading:0.2f}, {roll:0.2f}, {pitch:0.2f}, {pos_pitch:0.2f}, {pos_roll:0.2f}, {pitch_d:0.2f}, {roll_d:0.2f}")
        
        
finally:
    pwm.set_pwm_dc(M4_PATH, 0)
    pwm.set_pwm_dc(M3_PATH, 0)
    print("stopping motors and program")



