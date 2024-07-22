#configure macros for peripherals and pins

#analog sensor paths
ROLL_POT_PATH = "/sys/bus/iio/devices/iio:device0/in_voltage0_raw" # P9_39
PITCH_POT_PATH = "/sys/bus/iio/devices/iio:device0/in_voltage1_raw" # P9_40
ADC_REF_PATH = "/sys/bus/iio/devices/iio:device0/in_voltage2_raw" # P9_37

#SOC Temperature paths
CPU_TEMP_PATH = "/sys/devices/virtual/thermal/thermal_zone0/temp"

#I2C
IMU_BUS = 7
IMU_ADDR = 0x28

#pwm driver paths
PWM_CHIP_BASE = "/sys/class/pwm/pwmchip0/"
M4_CHANNEL = "pwm0"  # P8_19
M3_CHANNEL = "pwm1"  # P8_13
M4_PATH = f"{PWM_CHIP_BASE}{M4_CHANNEL}" #concatenate strings for full channel path
M3_PATH = f"{PWM_CHIP_BASE}{M3_CHANNEL}"
PWM_PERIOD_NS = 1000000  # 1ms (1kHz)
PWM_DC_MAX_NS = 900000  # set max allowable duty cycle to 90%

#gpio lines for motor direction control
M3_DIR_PIN = 375  # P8_14 M3
M4_DIR_PIN = 351  # P8_26 M4

#safety limits for potentiometers in raw adc values
ROLL_POT_MAX = 1900
ROLL_POT_MIN = 300

PITCH_POT_MAX = 1900
PITCH_POT_MIN = 300
