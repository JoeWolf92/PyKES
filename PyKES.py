from datetime import datetime
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
from TLPM import TLPM
import time

saveDirectory = ""

# Open and setup powermeter
tlPM = TLPM()
deviceCount = c_uint32()
tlPM.findRsrc(byref(deviceCount))

print("devices found: " + str(deviceCount.value))

resourceName = create_string_buffer(1024)

for i in range(0, deviceCount.value):
    tlPM.getRsrcName(c_int(i), resourceName)
    print(c_char_p(resourceName.raw).value)
    break

tlPM.close()

tlPM = TLPM()

tlPM.open(resourceName, c_bool(True), c_bool(True))

message = create_string_buffer(1024)
tlPM.getCalibrationMsg(message)
print(c_char_p(message.raw).value)

time.sleep(1)

power_measurements = []
transverse_position = []
longitudinal_position = []

# Open and setup motor controllers


# Begin scan

# Scan longitudinal

# Scan transverse

# Take power measurement
power =  c_double()
tlPM.measPower(byref(power))
power_measurements.append(power.value)
#transverse_position.append(TRANSVERSE POSITION)
#longitudinal_position.append(LONGITUDINAL POSITION)
#print(LONGITUDINAL POSITION)
#print(TRANSVERSE POSITION)
print(power.value)


# Clean up connections
tlPM.close()

# Fit data

# Plot results

print('Scan complete. Data saved to: ' + saveDirectory)