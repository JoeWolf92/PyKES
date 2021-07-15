# required modules
import time
import numpy as np
import serial
import io
import math
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.optimize import curve_fit
from time import gmtime, strftime

xMax = 25 #mm
xMin = 0 #mm
zMax = 25 #mm
zMin = 0 #mm
#xBigStart = 9.16 #mm
#xBigLimit = 9.23 #mm
xMidStart = 8.8 #mm
xMidLimit = 9.2 #mm
#xSmallStart = 9.79 #mm
#xSmallLimit = 9.84 #mm
xSmallStep = 0.0005 #mm = 0.5um
#xMidStep = 0.002 #mm = 2um
#xBigStep = 0.003 #mm = 3um
zStart = 0.9 #mm
zLimit = 0.4 #mm
#zStep50 = 0.05 #mm = 50um
#zStep10 = 0.01 #mm = 10um
#zStep5 = 0.005 #mm = 5um
#zStep3 = 0.003 #mm = 3um
#zStep2 = 0.002 #mm = 2um
zStep1 = -0.0005 #mm = 0.5um
xErr = 0.00025 #mm
zErr = 0.00025 #mm
print("Started at " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

#------------------Functions-------------------#
# KES function
def KES(x,a,b,c,d):
	return 0.5*a*erf(0.5*(x-b)/c)+d
# def KES(x,a,b,c,d,e,w):
#     return ( -a/( 1 + np.exp( b*np.sqrt(2)*(x - d)/w + c*np.sqrt(2)*pow((x-d)/w,3 ) ) ) ) + e
# Min function
def KESMin(x,a,b,c):
	return (a*a)+((b*b)/(a*a))*(x-c)*(x-c)
#Double Gaussian Test
def DGaus(x,a,b,c,d,e,f,g):
	return a*erf(0.5*(x-b)/c) + d*erf(0.5*(x-b-e)/f) + g
#--------------------Basic Setup---------------------#
z = zStart
#-----------------------------Begin Scan-----------------------------#
print("Begin scan")
nDecimals = 6
saveDirectory = "C:\\Users\\rbg94965\\Documents\\NewKES\\Objective\\SmallRangeFineReFit\\"
counter = 0
fullScanData = []
# while z < (zLimit + zStep1):
# while z >= (zLimit):
# 	#if z < 17.1 or z == 17.1:
# 	#	xStart = xBigStart
# 	#	xLimit = xBigLimit
# 	#	xStep = xBigStep
# 	#elif 17.1 < z < 17.165:
# 	#	xStart = xMidStart
# 	#	xLimit = xMidLimit
# 	#	xStep = xMidStep
# 	#elif z == 17.165 or 17.165 < z < 17.235 or z == 17.235:
# 	#	xStart = xSmallStart
# 	#	xLimit = xSmallLimit
# 	#	xStep = xSmallStep
# 	#elif 17.235 < z < 17.3:
# 	#	xStart = xMidStart
# 	#	xLimit = xMidLimit
# 	#	xStep = xMidStep
# 	#elif z == 17.3 or z > 17.3:
# 	#	xStart = xBigStart
# 	#	xLimit = xBigLimit
# 	#	xStep = xBigStep
# 	#else:
# 	#	xStart = xBigStart
# 	#	xLimit = xBigLimit
# 	#	xStep = xSmallStep
# 	xStart = xMidStart
# 	xLimit = xMidLimit
# 	xStep = xSmallStep
# 	# save scan results for this z value
# 	print("Saving scan for z="+str(z))
# 	resultsName = str(z) + '.txt'
# 	saveResults = np.loadtxt(saveDirectory + resultsName)
# 	# fit error function and find waist
# 	#p0 = np.array([0.0025,-1,-0.007,8.17,0.0025,0.01])#[-1.4e8,1e4,3e2,-1.4e8,10,3e2,2e7])
# 	p0 = np.array([-2.4e-3,8.99,0.0075,1.2e-3])#[-1.4e8,1e4,3e2,-1.4e8,10,3e2,2e7])
# 	try:
# 		#popt,pcov = curve_fit(DGaus,saveResults[:,0],saveResults[:,1],p0)		
# 		popt,pcov = curve_fit(KES,saveResults[:,0],saveResults[:,1],p0)
# 		#np.savetxt('Fits.txt',popt)
# 		waist = popt[2]/math.sqrt(2)
# 		# waist = popt[5]
# 		perr = np.sqrt(np.diag(pcov))
# 		#np.savetxt('Errors.txt',perr)
# 		waistErr = perr[2]/math.sqrt(2)
# 		fullScanData.append([z,waist*waist,2*(waistErr*waist)])
# 		xData = np.linspace(xStart,xLimit,10000)
# 		yData = KES(xData,*popt)
# 		# create and save graph of results
# 		plt.errorbar(saveResults[:,0],saveResults[:,1],saveResults[:,2],xErr, uplims=True, label="Experimental Data")
# 		plt.plot(xData,yData,"r",label="Theorectical Fit")
# 	except:
# 		print("Cannot find fit: excluding this result and moving on to next measurements, z="+ str(z))
# 		plt.errorbar(saveResults[:,0],saveResults[:,1],saveResults[:,2],xErr, uplims=True, label="Experimental Data")
# 	graphTitle = u'Knife edge scan at ' + str(z) + ' mm'
# 	xLabelKES = r'$Transverse\ Knife\ Edge\ Position\ (mm)$'#({\mu}m)$'
# 	yLabelKES = r'$Intensity$'
# 	saveFile = saveDirectory + str(z)+'.eps'
# 	plt.title(graphTitle)
# 	plt.xlabel(xLabelKES)
# 	plt.ylabel(yLabelKES)
# 	plt.legend(numpoints=1,loc=0)
# 	#plt.savefig(saveFile)
# 	saveFile = saveDirectory + str(z)+'.png'
# 	plt.savefig(saveFile)
# 	plt.clf()
# 	# increment z
# 	#counter = counter + 1
# 	#if counter < 21:
# 	#	z = z + zStep5
# 	#elif counter < 31:
# 	#	z = z + zStep3
# 	#elif counter < 51:
# 	z = round(z + zStep1, nDecimals)
# 	#elif counter < 61:
# 	#	z = z + zStep3
# 	#else:
# 	#	z = z + zStep5
# save full scan results
print("Saving full scan results")
resultsName = saveDirectory + 'FullScan.txt'
saveFullResults = np.loadtxt(resultsName) #np.array(fullScanData)#
# np.savetxt(resultsName,saveFullResults)
# fit minimum curve and find results
lowLim = 550
upLim = 625
saveFullResults = saveFullResults[lowLim:upLim,:]
zStart=max(saveFullResults[:,0])
zLimit=min(saveFullResults[:,0])
p0 = np.array([0.0005,0.00001,0.6])
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
	fitResultsName = saveDirectory + 'FullScanFitParaSmaller.txt'
	np.savetxt(fitResultsName,saveFitResults)
	# create and save final scan graph
	xData = np.linspace(zStart,zLimit,10000)
	yData = KESMin(xData,popt[0],popt[1],popt[2])
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr, uplims=True, label="Experimental Data")
	plt.plot(xData,yData,"r",label="Theorectical Fit")
except:
	print("Cannot find fit: Saving data and graph for seperate analysis.")
	plt.errorbar(saveFullResults[:,0],saveFullResults[:,1],saveFullResults[:,2],zErr, uplims=True, label="Experimental Data")
graphTitle = u'Knife edge scan through Rayleigh range'
xLabelKES = r'$Longitudinal\ Knife\ Edge\ Position\ (mm)$'#({\mu}m)$'
yLabelKES = r'$Waist\ size\ squared\ (mm^2)$'#({\mu}m^2)$'
saveFile = saveDirectory + 'FullScanSmaller.png'
plt.ylim(min(yData)*0.9,max(yData)*1.1)
plt.title(graphTitle)
plt.xlabel(xLabelKES)
plt.ylabel(yLabelKES)
plt.legend(numpoints=1,loc=0)
plt.savefig(saveFile)
#------------------Clean Up--------------------#
print("Scan finished at " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
plt.show()
