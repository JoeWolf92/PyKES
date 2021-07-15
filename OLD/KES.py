#-----------------------Settings----------------------#
# required modules
import time
import numpy as np
import pylibapogee.pylibapogee as apg
import pylibapogee.pylibapogee_setup as SetupDevice
import serial
import io
import math
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.optimize import curve_fit
from time import gmtime, strftime
import urllib2
# port settings
stagePort = '/dev/ttyUSB1'
xStage = '01'
zStage = '02'
xFindHome = xStage + 'OR\r\n'
zFindHome = zStage + 'OR\r\n'
xStatus = xStage + 'TS\r\n'
zStatus = zStage + 'TS\r\n'
# scan settings
xMax = 25 #mm
xMin = 0 #mm
zMax = 25 #mm
zMin = 0 #mm
#xBigStart = 9.16 #mm
#xBigLimit = 9.23 #mm
xMidStart = 9.800 #mm
xMidLimit = 9.855 #mm
#xSmallStart = 9.79 #mm
#xSmallLimit = 9.84 #mm
xSmallStep = 0.001 #mm = 1um
#xMidStep = 0.002 #mm = 2um
#xBigStep = 0.003 #mm = 3um
zStart = 17.260 #mm
zLimit = 17.300 #mm
#zStep50 = 0.05 #mm = 50um
#zStep10 = 0.01 #mm = 10um
#zStep5 = 0.005 #mm = 5um
#zStep3 = 0.003 #mm = 3um
#zStep2 = 0.002 #mm = 2um
zStep1 = 0.001 #mm = 1um
exposureLimitMax = 5 #s
exposureLimitMin = 0.02 #s
xErr = 0.25 #um
zErr = 0.25 #um
# saturation settings
maxSaturation = 45000 # res. 1024x1024
hiSatLimit = 0.95*maxSaturation
lowSatLimit = 0.85*maxSaturation
print "Started at ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
#-------------------Update Settings------------------#
updateFile = "/home/joewolf/Dropbox/ScanUpdate/update.txt"
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
#------------------Connect To Camera-----------------#
# look for ethernet cameras
print "Trying to find and connect with camera"
devices = SetupDevice.GetEthernetDevices()
# exception....no cameras anywhere....
if( len(devices) == 0 ):
    raise RuntimeError( "No devices found on ethernet" )
    stages.close()
# connect to the first camera
cam = SetupDevice.CreateAndConnectCam( devices[0] )
print "Camera connected"
#--------------Set And Check Camera Temp-------------#
# set cooler and wait for camera to reach temp
print "Setting camera temperature"
cam.SetCoolerSetPoint(-19)
cam.SetCooler( False )
cam.SetCooler( True )
Temp = cam.GetTempCcd()
print "The CCD Temperature is: ", Temp
while (Temp > -17):
	time.sleep(30)
	Temp = cam.GetTempCcd()
	print "The CCD Temperature is: ", Temp
print "Camera target temperature reached"
#------------------Functions-------------------#
# home stage
def homeStage(axis):
	stages.flush()
	stagesStatus = ''
	if axis == 'x':
		stages.write(xFindHome.encode('utf-8'))
		stages.flush()
		while str(stagesStatus) != '01TS000032\r\n':
			time.sleep(0.05)
			stages.write(xStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
	elif axis == 'z':
		stages.write(zFindHome.encode('utf-8'))
		stages.flush()
		while str(stagesStatus) != '02TS000032\r\n':
			time.sleep(0.05)
			stages.write(zStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
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
		while str(stagesStatus) != '01TS000033\r\n':
			time.sleep(0.05)
			stages.write(xStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
	elif axis == 'z':
		zMove = zStage + "PA" + str(distance) + "\r\n"
		stages.write(zMove.encode('utf-8'))
		stages.flush()
		while str(stagesStatus) != '02TS000033\r\n':
			time.sleep(0.05)
			stages.write(zStatus.encode('utf-8'))
			stagesStatus = stages.readline()
			stages.flush()
	else:
		raise ('Tried to MOVE unknown stage')
	return
# take image
def takeImage(exp,shutter):
	cam.StartExposure( exp, shutter )
	# wait for image
	status = None
	while status != apg.Status_ImageReady:
	    status = cam.GetImagingStatus()	
	    if( apg.Status_ConnectionError == status or
		apg.Status_DataError == status or
		apg.Status_PatternError == status ):
		msg = "Run %s: FAILED - error in camera status = %d" % (runStr, status)
		raise RuntimeError( msg )
	# get image
	print "Getting image"
	data = np.array([])
	data = cam.GetImage()
	return data
# KES function
def KES(x,a,b,c,d):
	return 0.5*a*erf(0.5*(x-b)/c)+d
# Min function
def KESMin(x,a,b,c):
	return (a*a)+((b*b)/(a*a))*(x-c)*(x-c)
# check internet connection
def internetOn():
    try:
        response=urllib2.urlopen('http://www.google.co.uk',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False
#--------------------Basic Setup---------------------#
# some basic info
print "Imaging rows = %d, columns = %d" % ( cam.GetMaxImgRows(), cam.GetMaxImgCols() )
cam.SetImageCount(1)
count = 0
# -----------CHANGED FOR TESTING----------
ImgCount = 2
# -----------CHANGED FOR TESTING----------
# find home for both stages
print "Setting both stages to home"
#homeStage('x')
#homeStage('z')
moveStage('x',9)
moveStage('z',17.2)
print "Stages set to home"
# set zStage to starting positions
z = zStart
#-----------------------------Begin Scan-----------------------------#
print "Begin scan"
counter = 0
fullScanData = []
# -----------CHANGED FOR TESTING----------
while z < (zLimit + zStep1):
# -----------CHANGED FOR TESTING----------
	print "Scan started at ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
	# set exposure time
	exposeTime = 0.04
	exposeTimeUse = round(exposeTime,3)
	# move zStage
	print "Moving z stage"
	moveStage('z',z)
	# data array
	results = []
#-------------------Scan Knife Edge------------------#
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
	# set xStage
	x = xStart
	previousMeasurement = 0
	while x < (xLimit + xStep):
		# move xStage
		print "Moving x stage"
		moveStage('x',x)
#-------------------Check Exposure-------------------#
		CorrectExp = False
		while CorrectExp != True:
			# take image
			print "Starting %f sec light exposure" % (exposeTime)
			exposeTimeUse = round(exposeTime,3)
			print "Exposure time rounded to %f sec" % (exposeTimeUse)
			expData = takeImage(exposeTimeUse,True)			
			# save image (NO NEED TO SAVE DURING LIVE)
			#print "Saving image to file"
			#imgName = 'ExpTest.txt'
			#np.savetxt(imgName,expData)
			# test exposure
			print "Testing saturation level"
			hiCond = expData > hiSatLimit
			lowCond = expData > lowSatLimit
			if exposeTime > exposureLimitMax:
				print "Maximum exposure limit reached"
				print "Exposure time set to ", exposeTime
				CorrectExp = True			
			elif len(np.extract(hiCond,expData)) > 1: # expLimit*len(expData):
				print "Saturated, reducing exposure time"
				exposeTime = exposeTime - 0.1*exposeTime
				if exposeTime == exposureLimitMin:
					print "Saturated at minimum exposure limit"
					stages.close()
					cam.SetCooler( False )
					cam.CloseConnection()
					raise RuntimeError( "Increase attenuation of ND filters to prevent damage to CCD" )
				elif exposeTime < exposureLimitMin:
					print "Minimum exposure limit reached"
					exposeTime = exposureLimitMin
				#exposeTime = round(exposeTime,2)
			elif len(np.extract(lowCond,expData)) < 1: #expLimit*len(expData):
				print "Signal level too low, increasing exposure time"
				exposeTime = exposeTime + 0.1*exposeTime
				#exposeTime = round(exposeTime,2)
			else:
				exposeTime = exposeTimeUse
				print "Exposure time set to ", exposeTimeUse
				CorrectExp = True
#--------------------Take Measurements---------------#		
		count = 0
		dataExp = []
		dataBg = []
		while count < ImgCount:
			# take image
			print "Taking image at x=", x, " and z=", z, " with texp=", exposeTime
			data = takeImage(exposeTime,True)
			# collect image data
			print "Collecting image data"
			dataExp.append(np.sum(data)/exposeTime)
			# take background image
			print "Taking background at x=", x, " and z=", z, " with texp=", exposeTime
			bgData = takeImage(exposeTime,False)
			# collect background data
			print "Collecting background data"
			dataBg.append(np.sum(bgData)/exposeTime)			
			count = count + 1
		print "Calculating and storing result"
		dataExpArray = np.array(dataExp)
		dataBgArray = np.array(dataBg)
		meanExp = np.mean(dataExpArray)
		errorExp = np.std(dataExpArray)
		meanBg = np.mean(dataBgArray)
		errorBg = np.std(dataBgArray)
		correctedExp = (meanExp - meanBg)
		correctedError = (math.sqrt(math.pow(errorExp,2)+math.pow(errorBg,2)))
		resultExp = [x*1000,correctedExp,correctedError]
		results.append(resultExp)
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
		x = x + xStep
	# 8 xStage to backoff backlash
	x = 8
	moveStage('x',x)
	# save scan results for this z value
	print "Saving scan"
	saveResults = np.array(results)
	resultsName = str(z) + '.txt'
	np.savetxt(resultsName,saveResults)
	# fit error function and find waist
	p0 = np.array([-2.7e8,1e4,3e2,2e7])
	try:
		popt,pcov = curve_fit(KES,saveResults[:,0],saveResults[:,1],p0)
		waist = popt[2]/math.sqrt(2)
		perr = np.sqrt(np.diag(pcov))
		waistErr = perr[2]/math.sqrt(2)
		fullScanData.append([z*1000,waist*waist,2*(waistErr*waist)])
		xData = np.linspace(xStart*1000,xLimit*1000,10000)
		yData = KES(xData,popt[0],popt[1],popt[2],popt[3])
		# create and save graph of results
		plt.errorbar(saveResults[:,0],saveResults[:,1],saveResults[:,2],xErr,markersize=5,label="Experimental Data",fmt='None')
		plt.plot(xData,yData,"r",label="Theorectical Fit")
	except:
		print "Cannot find fit: excluding this result and moving on to next measurements"

		plt.errorbar(saveResults[:,0],saveResults[:,1],saveResults[:,2],xErr,markersize=5,label="Experimental Data",fmt='None')
	graphTitle = u'Knife edge scan at ' + str(z) + ' mm'
	xLabelKES = r'${Transverse\ Knife\ Edge\ Position\ ({\mu}m)}$'
	yLabelKES = r'${Intensity}$'
	saveFile = str(z)+'.eps'
	plt.title(graphTitle)
	plt.xlabel(xLabelKES)
	plt.ylabel(yLabelKES)
	plt.legend(numpoints=1,loc=0)
	plt.savefig(saveFile)
	plt.clf()
###	with open(updateFile,"a") as myFile:
##		if internetOn():
#			intState = 'ON'
#		else:
#			intState = 'OFF'
#		timeNow = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
#		statement = 'Measurements finished at z=' + str(z) + ' and the internet connection was ' + intState + '.\n' + timeNow + '.\n'
#		myFile.write(statement)
	# increment z
	counter = counter + 1
# Changed for testing
#	if z < 17.23:
	z = z + zStep1
#	elif z > 17.26:
#		z = z + zStep2
#	else:
#		z = z + zStep1
	print "Scan finished at ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
# save full scan results
print "Saving full scan results"
saveFullResults = np.array(fullScanData)
resultsName = 'FullScan.txt'
np.savetxt(resultsName,saveFullResults)
# fit minimum curve and find results
p0 = np.array([1.3,5e-2,1.7e4])
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
	fitResultsName = 'FullScanFitPara.txt'
	np.savetxt(fitResultsName,saveFitResults)
	# create and save final scan graph
	xData = np.linspace(zStart*1000,(zLimit+zStep1)*1000,10000)
	yData = KESMin(xData,popt[0],popt[1],popt[2])
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,markersize=5,label="Experimental Data",fmt='None')
	plt.plot(xData,yData,"r",label="Theorectical Fit")
except:
	print "Cannot find fit: Saving data and graph for seperate analysis."
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,markersize=5,label="Experimental Data",fmt='None')
graphTitle = u'Knife edge scan through Rayleigh range'
xLabelKES = r'${Longitudinal\ Knife\ Edge\ Position\ ({\mu}m)}$'
yLabelKES = r'${Waist\ size\ squared\ ({\mu}m^2)}$'
saveFile = 'FullScan.eps'
plt.title(graphTitle)
plt.xlabel(xLabelKES)
plt.ylabel(yLabelKES)
plt.legend(numpoints=1,loc=0)
plt.savefig(saveFile)
#------------------Clean Up--------------------#
# close port
stages.close()
# close camera connectione
cam.SetCooler(False)
cam.CloseConnection()
print "Finished at ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
plt.show()
