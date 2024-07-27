from config import *
from control.PD_controller import PDController
from hardware.adc import read_adc
from hardware.pwm import PWMController
from hardware.gpio import GPIOControl
from utils.logger import testData # Import custom testData class

logger = testData() #create instance with current filename and time
#logger = testData(filename = 'test_pwm_pdctrl_testData.txt') #or enter manual name

pwm = PWMController(PWM_CHIP_BASE, PWM_PERIOD_NS)

gpio = GPIOControl()
gpio.setup_pin(351, direction='out', default_value=0)

controller = PDController(Kp=20, Kd=3, setpoint=350)

pos = read_adc(PITCH_POT_PATH)

while pos > 350:
    pos = read_adc(PITCH_POT_PATH)
    logger.log("position",pos)
    output = controller.compute(pos)
    logger.log("output",output)
    print(output)
    if output < 0:
        gpio.set_value(351, 0)
        pwm.set_pwm_dc(M4_PATH, abs(output))
    if output > 1:
        gpio.set_value(351,1)
        pwm.set_pwm_dc(M4_PATH, abs(output))
    pos = read_adc(PITCH_POT_PATH)
    #print(pos)
    
pwm.set_pwm_dc(M4_PATH, 0)

print("log file generated: " logger.filename)
#print(logger_auto.subscribe()) #or print logged data
        
