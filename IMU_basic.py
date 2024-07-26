import time
from Adafruit_BNO055 import BNO055

# Initialize the BNO055 and stop if something went wrong
bno = BNO055.BNO055(busnum=7)

if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
                       
# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test)) # Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}'.format(gyro))

# print('Reading BNO055 date, press Ctrl-C to quit...')

while True:
    # Read the Euler angles for heading, roll, pitch (all in deg)
    heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated
    # sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out
    print('Heading={0:0.2F} Pitch={1:0.2F} Roll={2:0.2F}'.format(heading, roll, pitch))
    # print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(heading, roll, pitch, sys, gyro, accel, mag))
