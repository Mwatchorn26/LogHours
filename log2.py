import time
import pdb
import win32gui

logPath = r'c:\Users\Michael Watchorn\LogHours\hours.log'

while True:
	fileHandle = open(logPath,"r")
	lineList = fileHandle.readlines()
	fileHandle.close()
	#print(lineList)
	lastTime=str(lineList[-1]).split(' ')[0]
	print("Last Time: %s" % lastTime)
	#pdb.set_trace()
	currentTime=str(time.time()).split('.')[0]
	print("Current Time: %r" % currentTime)
	difference = float(currentTime) - float(lastTime)
	print(str(difference))
	if (difference) > 12:
		print("")
		print("\n\nJust Restarted\n")
		with open(logPath,"a") as log:
			readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(currentTime)))
			log.write(str(currentTime)+ '  ' + readableTime+'\n')
		log.close()
		
		w=win32gui
		print(w.GetWindowText (w.GetForegroundWindow()))
		
	time.sleep(6)
