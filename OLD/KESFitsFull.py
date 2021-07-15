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

#------------------Functions-------------------#
# KES function
def KES(x,a,b,c,d):
	return 0.5*a*erf(0.5*(x-b)/c)+d
# Min function
def KESMin(x,a,b,c):
	return (a*a)+((b*b)/(a*a))*(x-c)*(x-c)
#--------------------Basic Setup---------------------#
z = zStart
#-----------------------------Begin Scan-----------------------------#
print "Begin scan"
counter = 0
fullScanData = []

# save full scan results
print "Saving full scan results"
resultsName = 'FullScanEdit.txt'
saveFullResults = np.loadtxt(resultsName)
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
	fitResultsName = 'FullScanFitParaEdit.txt'
	np.savetxt(fitResultsName,saveFitResults)
	# create and save final scan graph
	xData = np.linspace(zStart*1000,zLimit*1000,10000)
	yData = KESMin(xData,popt[0],popt[1],popt[2])
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,markersize=5,label="Experimental Data",fmt='None')
	plt.plot(xData,yData,"r",label="Theorectical Fit")
except:
	print "Cannot find fit: Saving data and graph for seperate analysis."
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr,markersize=5,label="Experimental Data",fmt='None')
graphTitle = u'Knife edge scan through Rayleigh range'
xLabelKES = u'$Longitudinal\ Knife\ Edge\ Position\ ({\mu}m)$'
yLabelKES = u'$Waist\ size\ squared\ ({\mu}m^2)$'
saveFile = 'FullScanEdit.eps'
plt.title(graphTitle)
plt.xlabel(xLabelKES)
plt.ylabel(yLabelKES)
plt.legend(numpoints=1,loc=0)
plt.savefig(saveFile)
#------------------Clean Up--------------------#
print "Finished at ", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
plt.show()
