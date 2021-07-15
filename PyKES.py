#/////////////// Packages //////////////////

from datetime import datetime
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
from TLPM import TLPM
import time
import numpy as np
import serial
import io
import math
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.optimize import curve_fit
from time import gmtime, strftime
# import urllib2

#//////////////// Start Timestamp ////////////////////

print("Started at " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

#///////////// Motor Controller Port Settings //////////////

stagePort = 'COM3'
xStage = '02'
zStage = '01'
xFindHome = xStage + 'OR\r\n'
zFindHome = zStage + 'OR\r\n'
xStatus = xStage + 'TS\r\n'
zStatus = zStage + 'TS\r\n'

#/////////////// Scan Parameters ////////////////////

xMax = 25 #mm
xMin = 0 #mm
zMax = 25 #mm
zMin = 0 #mm
#xBigStart = 9.16 #mm
#xBigLimit = 9.23 #mm
xMidStart = 8.8#8.1 #mm
xMidLimit = 9.2#8.25 #mm
#xSmallStart = 9.79 #mm
#xSmallLimit = 9.84 #mm
xSmallStep = 0.0005 #mm = 0.5um
#xMidStep = 0.002 #mm = 2um
#xBigStep = 0.003 #mm = 3um
zStart = 0.9#8.08 #mm
zLimit = 0.4#8.38 #mm
#zStep50 = 0.05 #mm = 50um
#zStep10 = 0.01 #mm = 10um
#zStep5 = 0.005 #mm = 5um
#zStep3 = 0.003 #mm = 3um
#zStep2 = 0.002 #mm = 2um
zStep1 = -0.0005 #mm = 0.5um
xErr = 0.00025 #mm = 0.25um
zErr = 0.00025 #mm = 0.25um

xResetStep = 0.5 #mm value to remove backlash on each x scan
zResetStep = -0.5 #mm value to remove backlash on each z scan

knifeEdgeBlockingPositionX = 13 #mm for background measurement
knifeEdgeBlockingPositionZ = 0.5 #mm for background measurement

multipleReadingsCount = 3
nDecimals = 6

#///////////////// Save Directory /////////////////

saveDirectory = "C:\\Users\\rbg94965\\Documents\\NewKES\\Objective\\SmallRangeFine\\"

#//////////////// Open and Initialise Powermeter ////////////////

tlPM = TLPM()
deviceCount = c_uint32()
tlPM.findRsrc(byref(deviceCount))

print("devices found: " + str(deviceCount.value))

resourceName = create_string_buffer(1024)

for i in range(0, deviceCount.value):
    tlPM.getRsrcName(c_int(i), resourceName)
    print(c_char_p(resourceName.raw).value)
    break

tlPM.open(resourceName, c_bool(True), c_bool(True))

message = create_string_buffer(1024)
tlPM.getCalibrationMsg(message)
print(c_char_p(message.raw).value)

#//////////////////// Initialise Results Arrays ///////////////////

powerMeasurements = []
transversePosition = []
longitudinalPosition = []

#////////////////// Open and Setup Motor Controllers ///////////////////

print("Connecting to stages port")
stages = serial.Serial(port=stagePort,
                baudrate=57600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.1)
if stages.isOpen():
	print("Port opened")
else:
	stages.close()
	stages.open()
	print("Port opened")

#///////////////// Functions ///////////////////

# home stage
def homeStage(axis):
	stages.flush()
	stagesStatus = ''
	if axis == 'x':
		stages.write(xFindHome.encode('utf-8'))
		stages.flush()
		time.sleep(1)
		while str(stagesStatus) != "b'02TS000032\\r\\n'" and str(stagesStatus) != "b'02TS000033\\r\\n'": #REMOVE HARDCODE
			time.sleep(0.05)
			stages.write(xStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
			print( "x " + str(stagesStatus))
	elif axis == 'z':
		stages.write(zFindHome.encode('utf-8'))
		stages.flush()
		time.sleep(1)
		while str(stagesStatus) != "b'01TS000032\\r\\n'" and str(stagesStatus) != "b'01TS000033\\r\\n'": #REMOVE HARDCODE
			time.sleep(0.05)
			stages.write(zStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
			print( "z " + str(stagesStatus))
	else:
		raise ('Tried to HOME unknown stage')
	return

# move stage
def moveStage(axis,distance):
	stages.flush()
	stagesStatus = ''
	if axis == 'x':
		xMove = xStage + "PA" + str(distance) + "\r\n"
		stages.write(xMove.encode('utf-8'))
		stages.flush()
		while str(stagesStatus) != "b'02TS000033\\r\\n'": #REMOVE HARDCODE
			time.sleep(0.05)
			stages.write(xStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
	elif axis == 'z':
		zMove = zStage + "PA" + str(distance) + "\r\n"
		stages.write(zMove.encode('utf-8'))
		stages.flush()
		while str(stagesStatus) != "b'01TS000033\\r\\n'": #REMOVE HARDCODE
			time.sleep(0.05)
			stages.write(zStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
	else:
		raise ('Tried to MOVE unknown stage')
	return

# KES function
def KES(x,a,b,c,d):
	return 0.5*a*erf(0.5*(x-b)/c)+d

# Min function
def KESMin(x,a,b,c):
	return (a*a)+((b*b)/(a*a))*(x-c)*(x-c)

# # check internet connection
# def internetOn():
#     try:
#         response=urllib2.urlopen('http://www.google.co.uk',timeout=1)
#         return True
#     except urllib2.URLError as err: pass
#     return False

#////////////////// Home Stages ////////////////

print("Setting both stages to home")
homeStage('x')
homeStage('z')
print("Stages set to home")

#////////////////// Begin scan ///////////////////

print("Taking background measurement")
x = knifeEdgeBlockingPositionX
z = knifeEdgeBlockingPositionZ
moveStage('x',x)
moveStage('z',z)
print("Background measurement at x=" + str(x) + " and z=" + str(z))
backgroundMeasurements = []
currentCount = 0

while currentCount < multipleReadingsCount:
	powerBackground =  c_double()
	tlPM.measPower(byref(powerBackground))
	backgroundMeasurements.append(powerBackground.value)
	currentCount = currentCount + 1

backgroundValue = np.mean(backgroundMeasurements)
backgroundError = np.std(backgroundMeasurements)

print("Reset z")
if zStart - zResetStep < zMin:
	z = zMin
else:
	z = round(zStart - zResetStep, nDecimals)
moveStage('z',z)
z = zStart

print("Begin scan")
startTime = time.time()
# Initialise Longitudinal Results Arrays
longitudinalPositions = []
waistFits = []
waistErrors = []
fullScanData = []

# Scan Longitudinal
# while z < (zLimit + zStep1):
while z >= (zLimit):
	# move zStage
	print("Moving z stage")
	moveStage('z',z)
	longitudinalPositions.append(z)
	# set x range settings depending on longitudinal position
    # Changed for testing
    #	if z < 17.23:
	xStart = xMidStart
	xLimit = xMidLimit
	xStep = xSmallStep
    #	elif z == 17.23 or 17.23 < z < 17.26 or z == 17.26:
    #		xStart = xSmallStart
    #		xLimit = xSmallLimit
    #		xStep = xSmallStep
    #	elif z > 17.26:
    #		xStart = xMidStart
    #		xLimit = xMidLimit
    #		xStep = xMidStep
    #	else:
    #		xStart = xMidStart
    #		xLimit = xMidLimit
    #		xStep = xSmallStep
	
    # Set xStage
	print("Reset x")
	if xStart - xResetStep < xMin:
			x = xMin
	else:
		x = round(xStart - xResetStep, nDecimals)
	moveStage('x',x)
	x = xStart
	# previousMeasurement = 0
    
    # Initialise Transverse Results Arrays
	powerMeasurements = []
	powerErrors = []
	backgroundMeasurements = []
	transversePositions = []

	while x < (xLimit + xStep):
		currentCount = 0
		# Move xStage
		print("Moving x stage")
		moveStage('x',x)
		transversePositions.append(x)
		print("Measurements at x=" + str(x) + " and z=" + str(z))
#///////////////// Take Measurements ///////////////#
		averagePowerMeasurements = []
		while currentCount < multipleReadingsCount:
            # Take Power Measurement
			power =  c_double()
			tlPM.measPower(byref(power))
			averagePowerMeasurements.append(power.value)
			currentCount = currentCount + 1

		powerMeasurements.append(np.mean(averagePowerMeasurements) - backgroundValue)
		powerErrors.append(math.sqrt(math.pow(np.std(averagePowerMeasurements),2)+math.pow(backgroundError,2)))
		
		# increment x
#		if previousMeasurement == 0:
#			xStep = xBigStep
#			print "Clause1: curMeas = "+str(correctedExp)+", preMeas = "+str(previousMeasurement)+", therefore xStep = "+str(xStep)
#		elif correctedExp < 0.95*previousMeasurement:
#			xStep = xSmallStep
#			print "Clause2: curMeas = "+str(correctedExp)+", preMeas = "+str(previousMeasurement)+", therefore xStep = "+str(xStep)
#		elif xStep == xSmallStep:
#			if correctedExp > 0.95*previousMeasurement:
#				xStep = xBigStep
#			else:
#				xStep = xSmallStep
#			print "Clause3: curMeas = "+str(correctedExp)+", preMeas = "+str(previousMeasurement)+", therefore xStep = "+str(xStep)
#		else:
#			xStep = xBigStep
#			print "Clause4: curMeas = "+str(correctedExp)+", preMeas = "+str(previousMeasurement)+", therefore xStep = "+str(xStep)
#		previousMeasurement = correctedExp
		x = round(x + xStep, nDecimals)
	# save scan results for this z value
	print("Saving scan")
	transverseResultsToSave = np.stack((transversePositions, powerMeasurements, powerErrors),axis=0).transpose()
	transverseResultsSaveName = str(z) + '.txt'
	np.savetxt(saveDirectory + transverseResultsSaveName, transverseResultsToSave)
	# fit error function and find waist
	p0 = np.array([-2.25e-3,9,1,1.1e-3])
	try:
		popt,pcov = curve_fit(KES,transverseResultsToSave[:,0],transverseResultsToSave[:,1],p0)
		waist = popt[2]/math.sqrt(2)
		perr = np.sqrt(np.diag(pcov))
		waistErr = perr[2]/math.sqrt(2)
		fullScanData.append([z,waist*waist,2*(waistErr*waist)])
		waistFits.append(waist)
		waistErrors.append(waistErr)
		xData = np.linspace(xStart,xLimit,10000)
		yData = KES(xData,*popt)
		# create and save graph of results
		plt.errorbar(transverseResultsToSave[:,0],transverseResultsToSave[:,1],transverseResultsToSave[:,2],xErr,uplims=True, label="Experimental Data")
		plt.plot(xData,yData,"r",label="Theorectical Fit")
	except:
		print("Cannot find fit: excluding this result and moving on to next measurements")

		plt.errorbar(transverseResultsToSave[:,0],transverseResultsToSave[:,1],transverseResultsToSave[:,2],xErr,uplims=True, label="Experimental Data")
	graphTitle = u'Knife edge scan at ' + str(z) + ' mm'
	xLabelKES = r'${Transverse\ Knife\ Edge\ Position\ (mm)}$'
	yLabelKES = r'${Intensity}$'
	saveFile = saveDirectory + str(z)+'.eps'
	plt.title(graphTitle)
	plt.xlabel(xLabelKES)
	plt.ylabel(yLabelKES)
	plt.legend(numpoints=1,loc=0)
	#plt.savefig(saveFile)
	saveFile = saveDirectory + str(z)+'.png'
	plt.savefig(saveFile)
	plt.clf()
	# increment z
    # Changed for testing
	# if z < 17.23:
	z = round(z + zStep1, nDecimals)
	# elif z > 17.26:
		# z = z + zStep2
	# else:
		# z = z + zStep1
	print("Scan finished at " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

# Clean up connections
tlPM.close()

print("Saving full scan results")
resultsName = saveDirectory + 'FullScan.txt'
saveFullResults = np.array(fullScanData)#np.loadtxt(resultsName)
np.savetxt(resultsName,saveFullResults)
# fit minimum curve and find results
p0 = np.array([10e-3,1e-3,8.24])
try:
	popt,pcov = curve_fit(KESMin,saveFullResults[:,0],saveFullResults[:,1],p0)
	waistMin = popt[0]
	waistPos = popt[2]
	waistFac = popt[1]
	perr = np.sqrt(np.diag(pcov))
	waistMinErr = perr[0]
	waistPosErr = perr[2]
	waistFacErr = perr[1]
	# save final results
	fitResults = []
	fitResults.append([waistMin,waistMinErr])
	fitResults.append([waistPos,waistPosErr])
	fitResults.append([waistFac,waistFacErr])
	saveFitResults = np.array(fitResults)
	fitResultsName = saveDirectory + 'FullScanFitPara.txt'
	np.savetxt(fitResultsName,saveFitResults)
	# create and save final scan graph
	xData = np.linspace(zStart,zLimit,10000)
	yData = KESMin(xData,popt[0],popt[1],popt[2])
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,uplims=True, label="Experimental Data")
	plt.plot(xData,yData,"r",label="Theorectical Fit")
except:
	print("Cannot find fit: Saving data and graph for seperate analysis.")
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,uplims=True, label="Experimental Data")
graphTitle = u'Knife edge scan through Rayleigh range'
xLabelKES = r'$Longitudinal\ Knife\ Edge\ Position\ (mm)$'#({\mu}m)$'
yLabelKES = r'$Waist\ size\ squared\ (mm^2)$'#({\mu}m^2)$'
saveFile = saveDirectory + 'FullScan.png'
plt.ylim(min(yData)*0.5,max(yData)*1.1)
plt.title(graphTitle)
plt.xlabel(xLabelKES)
plt.ylabel(yLabelKES)
plt.legend(numpoints=1,loc=0)
plt.savefig(saveFile)
#------------------Clean Up--------------------#
print("Scan finished at " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
print('Scan complete. Data saved to: ' + saveDirectory)
endTime = time.time()
print("Time taken: " + str(endTime - startTime))
plt.show()

