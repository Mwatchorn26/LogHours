import time
import string
import pdb
import win32gui
import operator
import os
import ctypes
import sys
from pathlib import Path

import win32api
import win32con
import win32evtlog
import win32security
import win32evtlogutil
 
class LogHours(object):
	def __init__(self):
		self.cleanBrowser = True

	def EventLogReportEvent(self):
		'''
		TODO THIS NEEDS TO INDICATE THAT THE LOGGING APPLICATION HAS STARTED, IT SHOULD NOT BE A WARNING.
		A SIMILAR PROCEDURE IS NEEDED WHEN A EXCEPTION OCCURS, AND DOCUMENT IT. THAT SHOULD BE A WARNING.
		'''
		print('\n\n\nReporting to Windows Event Log...')
		ph = win32api.GetCurrentProcess()
		th = win32security.OpenProcessToken(ph, win32con.TOKEN_READ)
		my_sid = win32security.GetTokenInformation(th, win32security.TokenUser)[0]

		applicationName = "Log Hours"
		eventID = 1
		category = 5	# Shell
		myType = win32evtlog.EVENTLOG_WARNING_TYPE
		descr = ["A warning", "An even more dire warning"]
		data = "Application\0Data".encode("ascii")

		win32evtlogutil.ReportEvent(applicationName, eventID, eventCategory=category, 
		eventType=myType, strings=descr, data=data, sid=my_sid)

	def initializeInternalVariables(self):
		'''SETUP ALL OUR BEGINNING STATE VARIABLES'''
		self.appPath = os.path.normpath("c:/Users/" + os.getlogin() + "/LogHours/")
		self.scanTime = 60 #SECONDS BETWEEN UPDATES
		self.previousTitle=""
		self.last15scans={}
		self.files={'Temp':'','Hours':'','15minSummary':'','Summary':''}
		self.setFolderPath()
		self.lineList = ''

	def summarizeToday(self):
		'''WRITE OUT A SUMMARY OF TODAY'S ACTIVIES, GROUPING INTO 15 MINUTE SEGMENTS'''
		#READ IN TODAY'S TASKS INFO
		fileHandle = open(files['15minSummary'],"r")
		self.lineList = fileHandle.readlines()
		fileHandle.close()
		self.taskList={}
		self.calculateTodaysSummary()
		self.writeTodaysSummaryToFile()

	def calculateTodaysSummary():
		'''
		Create a list of tasks for today
		'''
		#CALCULATE TODAY'S SUMMARY
		for line in self.lineList:
			lineParts = line.split("Window:")
			self.title = lineParts[1]
			#UPDATE THE DICTIONARY WITH THIS TASK's TITLE 
			if self.title in taskList:
				self.taskList[title] = self.taskList[title]+1
				#print('Incremented summary time spent on %s' % title)
			else:
				self.taskList[title]=1
				#print('Added new task: %s' % title)

	def writeTodaysSummaryToFile(self):
		'''
		Overrite the summary file for today.
		'''
		#WRITE TODAY'S SUMMARY
		with open(self.files['Summary'],"w") as summary:
			try:
				for task in self.taskList:
					summary.write(str(0.25 * self.taskList[task]) + ' hrs on ' + str(task))
				summary.write("\n" + str(sum(self.taskList.values()) * 0.25 ) + " Hours Total")
				summary.close()
			except:
				print('Error occured!')

	def setFolderPath(self):
		#print('calling setFolderPath')
		day = time.strftime('%Y-%m-%d', time.localtime(time.time()))

		appPathDay = os.path.join(os.sep, self.appPath, day)	
		if not os.path.exists(appPathDay):
			os.makedirs(appPathDay)
		
		self.files['Temp'] = os.path.join(os.sep, self.appPath, 'temp')
		self.files['Hours'] = os.path.join(os.sep, self.appPath, 'hours.log')
		self.files['Latest'] = os.path.join(os.sep, self.appPath, 'latest.log')
		self.files['allTaskChanges'] = os.path.join(os.sep, self.appPath, day, 'allTaskChanges.log')
		self.files['15minSummary'] = os.path.join(os.sep, self.appPath, day, '15minuteSummary.log')
		self.files['Summary'] = os.path.join(os.sep, self.appPath, day, 'dailySummary.log')

		for key in self.files:
			self.open_or_create(key)
		
	def open_or_create(self, filename: str):
		'''OPEN OR CREATE A FILE (IF IT DOESN'T ALREADY EXIST)'''
		filePath = Path(self.files[filename])
		filePath.touch(exist_ok=True)
		fileHandle = open(filePath)
		fileHandle.close()

	def isSystemLocked(self):
		'''DETERMINE IF THE COMPUTER IS LOCKED (REQUIRING A USER TO LOGIN)'''
		user32 = ctypes.windll.User32
		OpenDesktop = user32.OpenDesktopW #OpenDesktopA 
		SwitchDesktop = user32.SwitchDesktop
		DESKTOP_SWITCHDESKTOP = 0x0100

		hDesktop = OpenDesktop (u"default", 0, False, DESKTOP_SWITCHDESKTOP)
		#hDesktop = OpenDesktop ("default", 0, False, DESKTOP_SWITCHDESKTOP)
		result = SwitchDesktop (hDesktop)
		#if result:
		#	print "Unlocked"
		#	time.sleep (1.0)
		#else:
		#	print time.asctime (), "still locked"
		#	time.sleep (2)
		return not result

	def getData(self):
		'''GET THE SYSTEM DATA WE NEED TO DO OUR JOB'''
		self.readInLatestInfo()
		self.getTimes()
		self.getActiveWindowTitle()
		self.readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(currentTime)))
	
	def readInLatestInfo(self):
		'''READ IN THE PREVIOUS INFO'''
		try:
			fileHandle = open(self.files['Latest'],"r")
			LatestInfo = fileHandle.readlines()
		except:
			print('EXCEPTION:')
			print("title: %s" % self.title)
			print("Unexpected error:", sys.exc_info()[0])
		finally:
			fileHandle.close()
		self.lineList = LatestInfo

	def getTimes(self):
		'''GET THE LAST RECORDED TIME, AND THE CURRENT TIME, AND THE DIFFERENCE'''
		self.lastTime=str(self.lineList[-1]).split(' ')[0]
		#lastTime=str(lineList).split(' ')[0]
		#print("Last Time: %s" % lastTime)
		
		#GET THE CURRENT TIME
		self.currentTime=str(time.time()).split('.')[0]
		#print("Current Time: %r" % currentTime)

		#CALCULATE THE DIFFERENCE IN TIMES
		self.difference = float(self.currentTime) - float(self.lastTime)

	def appendToLog(self, textToLog):
		'''ADD textToLog TO LIST OF ALL TASK CHANGES'''
		with open(self.files['allTaskChanges'],"a") as log:
			log.write(textToLog)
			log.close()
		self.previousTitle = self.title

	def getActiveWindowTitle(self):
		'''Get the Window Title'''
		w=win32gui

		try:
			title = w.GetWindowText (w.GetForegroundWindow())
			print(title)
		except:
			print('EXCEPTION:')
			print("title: %r" % title)
			print("Unexpected error:", sys.exc_info()[0])
			title=""
		
		if self.cleanBrowser:
			#Throw out any web-page specific info, all we want is meta data.
			if 'Chrome'.lower() in title.lower(): 
				title="Chrome"
				#print("found Chrome")
			if 'Firefox'.lower() in title.lower(): 
				title="Firefix"
				#print("found FireFox")
			if 'Internet Explorer'.lower() in title.lower(): 
				title="Internet Explorer"
				#print("found IE")
		#print("Window Text: " + repr(title)+'\n')
		self.title = title

	def checkForRestart(self):
		'''CHECK FOR A TIME DISCREPENCY (Like when the program has crashed for a long time, and is restarted)'''
		if (self.difference)>(self.scanTime*2):
			self.setFolderPath()
			self.appendToLog('Started at: ' + str(self.currentTime)+ '  ' + self.readableTime + "\n", self.title, self.previousTitle)
			#previousTitle = title

	def checkForTaskChangeAndLock(self):
		'''CHECK FOR A CHANGE IN TASKS'''
		if (self.previousTitle != self.title):
			self.appendToLog(str(self.currentTime) + '  ' + self.readableTime + ' Window:' + self.title + "\n")
			#previousTitle = title
			if self.isSystemLocked():
				time.sleep(self.scanTime)
				return True  #System is Locked, sleep was reset, restart while loop
		return False # not locked

	def updateDict(self):
		'''UPDATE THE DICTIONARY WITH THE LATEST MINUTE'S TITLE'''
		if self.title in self.last15scans:
			self.last15scans[self.title]=self.last15scans[self.title]+1
			#print('Incremented time spent on %s' % title)
		else:
			self.last15scans[self.title]=1
			#print('Added new task: %s' % title)

	def fifteenMinuteLog(self):
		'''IF IT'S BEEN MORE THAN 15 MINUTES...'''
		if (sum(self.last15scans.values()) >= 15):
			mainTask = max(self.last15scans, key=lambda key: self.last15scans[key])
			#print("\nPast 15 minutes, main task:%r\n" % mainTask)
			self.last15scans={} #clear the scratch pad used to track the last 15 scans.
			with open(self.files['15minSummary'],"a") as log:
				log.write(str(self.currentTime)+ '  ' + self.readableTime + ' Window:' + self.mainTask + "\n")
				log.close()
			
			sys.stdout.write("-")
			sys.stdout.flush()

	def writeLatestValuesToTempFile(self):
		'''WRITE THE LATEST VALUES TO TEMPORARY FILE'''
		with open(self.files['Latest'],"w") as temp:
			try:
				temp.write(str(self.currentTime)+ '  ' + self.readableTime + ' Window:' + self.title)
			except:
				print('EXCEPTION:')
				print("title: %r" % self.title)
				print("Unexpected error:", sys.exc_info()[0])
			finally:
				temp.close()
		

def main():
	lh  = LogHours()
	#sysTray = SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)
	lh.EventLogReportEvent()
	lh.initializeInternalVariables()

	# try:
	# 	fileHandle = open(files['Latest'], 'r')
	# except Exception as e:
	# 	print(e)
	# # except IOError:
	# # 	with open(files['Latest'],"w") as fileHandle:
	# # 		fileHandle.write("Error Reading File")
	# fileHandle.close()

	while True:
		lh.getData()

		lh.checkForRestart()
		
		if lh.checkForTaskChangeAndLock():
			continue #System is Locked, sleep was reset, restart while loop

		lh.updateDict()

		lh.fifteenMinuteLog()

		#WRITE THE LATEST VALUES TO TEMPORARY FILE	
		lh.writeLatestValuesToTempFile()	
		
		#SUMMARIZE TODAY, JUST IN CASE WE LOSE POWER NOW
		lh.summarizeToday()
		
		sys.stdout.write(".")
		sys.stdout.flush()
		
		time.sleep(lh.scanTime)

if __name__ == "__main__":
    main()