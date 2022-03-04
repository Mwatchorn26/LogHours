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

	
#SETUP ALL OUR BEGINNING STATE VARIABLES
user = os.getlogin()
appPath = os.path.normpath("c:/Users/" + user + "/LogHours/")
scanTime = 60 #SECONDS BETWEEN UPDATES
previousTitle=""
last15scans={}
files={'Temp':'','Hours':'','15minSummary':'','Summary':''}


def summarizeToday():
    #print('Summarizing Today')
    #READ IN TODAY'S TASKS INFO
    fileHandle = open(files['15minSummary'],"r")
    lineList = fileHandle.readlines()
    fileHandle.close()
	
    taskList={}
    #CALCULATE TODAY'S SUMMARY
    for line in lineList:
        lineParts = line.split("Window:")
        title = lineParts[1]
        #UPDATE THE DICTIONARY WITH THIS TASK's TITLE 
        if title in taskList:
            taskList[title]=taskList[title]+1
            #print('Incremented summary time spent on %s' % title)
        else:
            taskList[title]=1
            #print('Added new task: %s' % title)
    newvar = "astercraft"
    #WRITE TODAY'S SUMMARY
    with open(files['Summary'],"w") as summary:
        try:
            for task in taskList:
                summary.write(str(0.25 * taskList[task]) + ' hrs on ' + str(task))
            summary.write("\n" + str(sum(taskList.values()) * 0.25 ) + " Hours Total")
            summary.close()
        except:
            print('Error occured!')

def setFolderPath(files):
	#print('calling setFolderPath')
	day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
		
	if not os.path.exists(appPath+'/'+day):
		os.makedirs(appPath+'/'+day)
	
	files['Latest'] = os.path.join(os.sep, appPath, 'latest.log')
	files['allTaskChanges'] = os.path.join(os.sep, appPath, day, 'allTaskChanges.log')
	files['15minSummary'] = os.path.join(os.sep, appPath, day, '15minuteSummary.log')
	files['Summary'] = os.path.join(os.sep, appPath, day, 'dailySummary.log')

	for key in files:
		open_or_create(key)
	
def open_or_create(filename: str):

	filePath = Path(filename)
	filePath.touch(exist_ok=True)
	fileHandle = open(filePath)
	fileHandle.close()
	#return fileHandle

def isSystemLocked():
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
	
	
print('\n\n\nInitializing...')
setFolderPath(files)
#print(files['Latest'])
#print(files['allTaskChanges'])
#print(files['15minSummary'])
#print(files['Summary'])

#pdb.set_trace()

# try:
# 	latest = open(r"c:\Users\m_wat\LogHours\latest",'w')
# 	latest.write("some text")
# except Exception as e:
# 	print(e)
# finally:
# 	latest.close()

try:
	fileHandle = open(files['Latest'], 'r')
except Exception as e:
	print(e)
# except IOError:
# 	with open(files['Latest'],"w") as fileHandle:
# 		fileHandle.write("Error Reading File")
fileHandle.close()

while True:
	
	#READ IN THE PREVIOUS INFO
	fileHandle = open(files['Latest'],"r")
	lineList = fileHandle.readlines()
	fileHandle.close()
	#print(lineList)
	#print(files['Latest'])
	
	#GET THE LAST RECORDED TIME
	lastTime=str(lineList[-1]).split(' ')[0]
	#lastTime=str(lineList).split(' ')[0]
	#print("Last Time: %s" % lastTime)
	
	#GET THE CURRENT TIME
	currentTime=str(time.time()).split('.')[0]
	#print("Current Time: %r" % currentTime)


	#sys.stdout.write(float(currentTime), ' ', float(lastTime))
	#sys.stdout.flush()
	#input ("\nPress any key to continue...")

    
	
	#CALCULATE THE DIFFERENCE IN TIMES
	difference = float(currentTime) - float(lastTime)

	#print(difference)
	
	#input("\n Waiting...")
    
	#Get the Window Title
	w=win32gui

	try:
		title = w.GetWindowText (w.GetForegroundWindow())
		testTitle= str(title)
	except:
		print('EXCEPTION:')
		print("title: %r" % title)
		print("Unexpected error:", sys.exc_info()[0])
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
	
	#pdb.set_trace()
	readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(currentTime)))
		
	#CHECK FOR A TIME DISCREPENCY
	if (difference)>(scanTime*2):	
		#print("\n\nRestarted\n")
		setFolderPath(files)
		with open(files['allTaskChanges'],"a") as log:
			log.write('Started at: ' + str(currentTime)+ '  ' + readableTime + "\n")
			#log.write(str(currentTime)+ '  ' + readableTime + ' Window:' + title + "\n")
			log.close()
		previousTitle = title
	
	#CHECK FOR A CHANGE IN TASKS
	if (previousTitle != title):
		#print("Task Changed")	
		with open(files['allTaskChanges'],"a") as log:
			log.write(str(currentTime)+ '  ' + readableTime + ' Window:' + title + "\n")
			log.close()
		previousTitle = title
		if isSystemLocked():
			#print('Detected System Locked')
			time.sleep(scanTime)
			continue

	#UPDATE THE DICTIONARY WITH THE LATEST MINUTE'S TITLE
	if title in last15scans:
		last15scans[title]=last15scans[title]+1
		#print('Incremented time spent on %s' % title)
	else:
		last15scans[title]=1
		#print('Added new task: %s' % title)
		
	#IF IT'S BEEN MORE THAN 15 MINUTES...
	if (sum(last15scans.values()) >= 15):
		mainTask = max(last15scans, key=lambda key: last15scans[key])
		#print("\nPast 15 minutes, main task:%r\n" % mainTask)
		last15scans={}		
		with open(files['15minSummary'],"a") as log:
			log.write(str(currentTime)+ '  ' + readableTime + ' Window:' + mainTask + "\n")
			log.close()
		
		sys.stdout.write("-")
		sys.stdout.flush()
		
		
	#WRITE THE LATEST VALUES TO TEMPORARY FILE
	with open(files['Latest'],"w") as temp:
		try:
			temp.write(str(currentTime)+ '  ' + readableTime + ' Window:' + title)
		except:
			print('EXCEPTION:')
			print("title: %r" % title)
			print("Unexpected error:", sys.exc_info()[0])
		temp.close()
		
	#SUMMARIZE TODAY, JUST IN CASE WE'RE SHUTDOWN THIS INSTANT
	summarizeToday()
	
	sys.stdout.write(".")
	sys.stdout.flush()
	
	time.sleep(scanTime)
