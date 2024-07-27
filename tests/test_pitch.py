from config import *
from control.PD_controller import PDController
from hardware.adc import read_adc
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
from utils.logger import tesData # Import custom logger class

logger = testData() # Generate test data log with test name and timestamp
#logger = testData(filename = 'test_pitch_test00') #or enter filename manually

pos_I = read_adc(PITCH_POT_PATH)  # Read initial position of pitch motor
controller = PDController(Kp=1, Kd=1, setpoint=pos_I)  # Initialize PD controller for pitch motor with gains
pwm = PWMController(PWM_CHIP_BASE, PWM_PERIOD_NS)  # Initialize PWM controller for pitch motor

gpio = GPIOControl()  # Initialize GPIO controller
gpio.setup_pin(351, direction='out', default_value=0)# Setup pin 351 P8_26
gpio.setup_pin(375, direction='out', default_value=0)# Setup pin 375 P8_14

pos_min, pos_max = None, None  # Initialize position variables
pos_tol = 5  # Define tolerance for position comparison

while True:

    if pos_I < 1000 and pos_min is None:  # Drive to the stop limit closest to start position
        setpoint = ROLL_POT_MIN + 10  # Add a little safety margin to the stop limit value measured earlier
        controller.set_setpoint(setpoint)
        pos = read_adc(PITCH_POT_PATH)
        logger.log("position",pos)
        while PITCH_POT_MIN < pos < setpoint:
            pos = read_adc(PITCH_POT_PATH)
            output_c = controller.compute(pos)
            logger.log("position",pos)
            logger.log("output_c",output_c)
            if output_c > 0:
                gpio.set_value(M4_DIR_PIN ,1)  # Set direction pin to high
                pwm.set_pwm_dc(M4_PATH, output_c)
            elif output_c < 0:
                gpio.set_value(M4_DIR_PIN ,0)  # Set direction pin to low
                pwm.set_pwm_dc(M4_PATH, abs(output_c))
            pos_min = pos  # Update pos_min

    if pos_I > 1000 and pos_max is None:
        pos = read_adc(PITCH_POT_PATH)
        logger.log("position",pos)
        setpoint = ROLL_POT_MAX - 10
        controller.set_setpoint(setpoint)
        while setpoint < pos < PITCH_POT_MAX:
            pos = read_adc(PITCH_POT_PATH)
            output_c = controller.compute(pos)
            logger.log("position",pos)
            logger.log("output_c",output_c)
            if output_c > 0:
                gpio.set_value(M4_DIR_PIN, 1)
                pwm.set_pwm_dc(M4_PATH, output_c)
            elif output_c < 0:
                gpio.set_value(M4_DIR_PIN, 0)
                pwm.set_pwm_dc(M4_PATH, abs(output_c))
            pos_max = pos  # Update pos_max

    # Drive to the midpoint of the total pitch travel
    if pos_min is not None and pos_max is not None:
        pos_F = (pos_max + pos_min) / 2
        logger.log("midpoint position", pos_F)
        controller.set_setpoint(pos_F)

        while abs(pos - pos_F) > pos_tol: #drive to the midpoint with some tolerance
            pos = read_adc(PITCH_POT_PATH)
            output_c = controller.compute(pos)
            logger.log("position",pos)
            logger.log("output_c",output_c)
            if output_c > 0:
                gpio.set_value(M4_DIR_PIN, 1)
                pwm.set_pwm_dc(M4_PATH, output_c)
            elif output_c < 0:
                gpio.set_value(M4_DIR_PIN, 0)
                pwm.set_pwm_dc(M4_PATH, abs(output_c))

    pwm.set_pwm_dc(M4_PATH, 0)  # Disable PWM channel to stop motor
    
    break  #exit condition to break the main loop
