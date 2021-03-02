#-----------------------Settings----------------------#
# required modules
import serial
import io
# port settings
stagePort = 'COM3'
xStage = '01'
zStage = '02'
xFindHome = xStage + 'OR\r\n'
zFindHome = zStage + 'OR\r\n'
xStatus = xStage + 'TS\r\n'
zStatus = zStage + 'TS\r\n'
#------------------Connect To Stages-----------------#
# open stage port
print "Connecting to stages port"
stages = serial.Serial(port=stagePort,
                baudrate=57600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.1)
if stages.isOpen():
	print "Port opened"
else:
	stages.close()
	stages.open()
	print "Port opened"
#------------------Reset Stages-----------------#
stages.write('01RS\r\n'.encode('utf-8'))
stages.write('02RS\r\n'.encode('utf-8'))
print "Stages reset"
#------------------Clean Up--------------------#
stages.close()
print "Port closed"