#import pywinauto
from LogApp.log import LogHours
import pytest
import os
import time
import inspect

# Fixtures

@pytest.fixture
def logHours():
    return LogHours()

@pytest.fixture
def logHours_internal_vars(logHours):
    
    logHours.initializeInternalVariables()
    return LogHours()

def setup_for_appendToLog(logHours, name_of_test):
    currentTime_test=str(time.time()).split('.')[0]
    ONE_HOUR = 60*60
    logHours.currentTime=str(float(currentTime_test) - ONE_HOUR)
    logHours.readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(logHours.currentTime)))
    logHours.title = name_of_test
    sample_text = name_of_test + '_pyTest at: ' + str(logHours.currentTime)+ ' ' + logHours.readableTime + ' Window: ' + logHours.title + "\n"
    return sample_text

#Tests
def test_appendToLog(logHours):
    from pathlib import Path
    import time
    import inspect
    #Prepare...
    full_text = f"""Mary had a little lamb.
    Who's fleece was white as snow. Window: {logHours.title} \n"""
    print(full_text)
    logHours.initializeInternalVariables()
    #should have been done in intitializeInternalvariables: logHours.setFolderPath()
    p = Path(logHours.files['allTaskChanges'])
    p.write_text("Mary had a little lamb.\n")

    #Run appendToLog
    logHours.appendToLog("    Who's fleece was white as snow. Window: " + logHours.title + " \n")
    
    #Examine the result
    assert p.read_text() == full_text

    #Append proper data
    name_of_test = inspect.stack()[0][3]
    sample_text = setup_for_appendToLog(logHours, name_of_test)
    logHours.appendToLog(sample_text)

@pytest.mark.skip(reason="incomplete")
def test_calculateTodaysSummary():
    pass

def test_checkForRestart(logHours):
    from pathlib import Path
    import inspect
    import time

    #Setup for assertion 1
    logHours.initializeInternalVariables()
    #should have been done in intitializeInternalVariables: logHours.setFolderPath()
    #logHours.readInLatestInfo() #REMOVED
    logHours.readInAllChanges() #ADDED
    logHours.getTimes()

    name_of_test = inspect.stack()[0][3]
    sample_text = setup_for_appendToLog(logHours, name_of_test)
    # currentTime_test=str(time.time()).split('.')[0]
    # ONE_HOUR = 60*60
    # logHours.currentTime=str(float(currentTime_test) - ONE_HOUR)
    # logHours.readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(logHours.currentTime)))
    # sample_text = name_of_test + ' pyTest at: ' + str(logHours.currentTime)+ '  ' + logHours.readableTime + "\n"
    # logHours.title = name_of_test

    logHours.appendToLog(sample_text)
    smallDelta = 1
    logHours.difference = logHours.scanTime - smallDelta
    expected = sample_text

    #Run function under test:
    logHours.checkForRestart()
    
    #Retrieve Actual
    fh = open(logHours.files['allTaskChanges'],'r')
    lines_from_file = fh.readlines()
    fh.close()
    actual = lines_from_file[-1]
    
    #Make assertion 1
    assert actual == expected


    #Setup for assertion 2
    logHours.difference = logHours.scanTime*3
    
    #Run function under test:
    logHours.checkForRestart()

    #Retrieve Actual
    fh = open(logHours.files['allTaskChanges'])
    lines_from_file = fh.readlines()
    fh.close()
    most_resent_entry = lines_from_file[-1]
    eleven_first_characters = most_resent_entry[:11]
    actual = eleven_first_characters
    expected = 'Started at:'

    #Make assertion 2
    assert actual == expected

@pytest.mark.skip(reason="incomplete")
def test_checkForTaskChangeAndLock(logHours):
    pass

@pytest.mark.skip(reason="incomplete")
def test_fifteenMinuteLog(logHours):
    pass

def test_getActiveWindowTitle(logHours):
    '''Compare [expected] hard-coded expected value to [actual] code result. Test title expected'''
    expected = 'test_log.py - LogHours - Visual Studio Code' #w.GetWindowText(window)
    
    logHours.getActiveWindowTitle()
    actual = logHours.title
    assert actual == expected

def test_getData(logHours):
    logHours.initializeInternalVariables()
    logHours.getData()

    #logHours.readableTime[:5]
    #(2022-03-08 08:42:39)
    #0         1         2
    #012345678901234567890
    assert logHours.readableTime[0] == '('
    assert logHours.readableTime[1:4].isdigit()
    assert logHours.readableTime[5] == '-'
    assert logHours.readableTime[6:7].isdigit()
    assert logHours.readableTime[8] == '-'
    assert logHours.readableTime[9:10].isdigit()
    assert logHours.readableTime[11] == ' '
    assert logHours.readableTime[12:13].isdigit()
    assert logHours.readableTime[14] == ':'
    assert logHours.readableTime[15:16].isdigit()
    assert logHours.readableTime[17] == ':'
    assert logHours.readableTime[18:19].isdigit()
    assert logHours.readableTime[20] == ')'
    

def test_getTimes(logHours):
    import time
    import inspect
    #START SETUP
    logHours.initializeInternalVariables()
    name_of_test = inspect.stack()[0][3] #A little introspective hacking to get the name of this function.
    sample_text = setup_for_appendToLog(logHours, name_of_test)

    # logHours.title = name_of_test
    # #Append dummy data
    # currentTime_test = str(time.time()).split('.')[0]
    # logHours.currentTime = currentTime_test
    # logHours.readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(logHours.currentTime)))
    #pyTest_lastTime = name_of_test + ' pyTest at: ' + str(logHours.currentTime)+ '  ' + logHours.readableTime + "\n"
    logHours.appendToLog(sample_text)

    #Read in latested dummy data
    #logHours.readInLatestInfo() #REMOVED
    logHours.readInAllChanges() #ADDED

    time.sleep(1)
    #END SETUP

    #RUN THE FUNCTION UNDER TEST, this creates a new currentTime:
    logHours.getTimes()

    #CHECK ASSERTS NOW
    #checking the "currentTime"
    actual = logHours.currentTime
    expected_currentTime = str(time.time()).split('.')[0]
    assert logHours.currentTime <= expected_currentTime

    #checking the "lastTime"
    actual = logHours.lastTime
    expected_lastTime = sample_text.split(' ')[2]
    assert actual == expected_lastTime

    #checking the difference:
    actual = logHours.difference
    expected_difference = float(logHours.currentTime) - float(expected_lastTime)
    assert actual == expected_difference

    #Assert the line has the proper number of columns (separated by spaces)
    actual = len(sample_text.split(' '))
    expected_length = 7
    assert actual == expected_length

def test_initializeInternalVariables(logHours):
    import os
    #logHours = LogHours()
    logHours.initializeInternalVariables()
    assert logHours.appPath == os.path.normpath("c:/Users/" + os.getlogin() + "/LogHours")
    assert logHours.appPath == "c:\\Users\\m_wat\\LogHours"
    assert logHours.scanTime == 60 #SECONDS BETWEEN UPDATES
    assert logHours.previousTitle == ""
    assert logHours.last15scans == {}
    #assert LogHours.files=={'Temp':'','Hours':'','15minSummary':'','Summary':''}
    #assert LogHours.setFolderPath() Asserted in it's own Test function.
    assert logHours.lineList == ''
    assert logHours.title == 'unassigned'
    
@pytest.mark.skip(reason="broken, and you'd have to send Win+L command to lock the system")
def test_isSystemLocked(logHours):
    def help_check_for_lock():
        import ctypes
        import time
        user32 = ctypes.windll.User32
        # import pywinauto
        # pywinauto.sendkeys(WIN+L)
        time.sleep(5)
        #
        #print(user32.GetForegroundWindow())
        #
        if (user32.GetForegroundWindow() % 10 == 0): 
            #print('Locked')
            return True
        # 10553666 - return code for unlocked workstation1
        # 0 - return code for locked workstation1
        #
        # 132782 - return code for unlocked workstation2
        # 67370 -  return code for locked workstation2
        #
        # 3216806 - return code for unlocked workstation3
        # 1901390 - return code for locked workstation3
        #
        # 197944 - return code for unlocked workstation4
        # 0 -  return code for locked workstation4
        #
        else: 
            #print('Unlocked')
            return False
    
    #import time
    #time.sleep(5)
    actual = logHours.isSystemLocked()
    expected = help_check_for_lock()
    assert actual == expected

@pytest.mark.skip(reason="incomplete")
def test_open_or_create():
    pass

@pytest.mark.skip(reason="OBSOLETE")
def test_readInLatestInfo(logHours):
    # from pathlib import Path
    # #fileHandle = open(self.files['Latest'],"w")
    # ##open(files['Latest'],"w") as fileHandle:
	# # fileHandle.write("Mary had a little lamb.\n")
	# # fileHandle.close()
    # sample_text = "Mary had a little lamb.\n"
    # logHours.initializeInternalVariables()
    # p = Path(logHours.files['Latest'])
    # #os.remove(p)
    # Path.unlink(p)
    # p.write_text(sample_text)
    # expected = [sample_text]

    # logHours.readInLatestInfo()
    # actual = logHours.lineList
    # assert actual == expected
    pass

def test_readInAllChanges(logHours):
    from pathlib import Path
    import time
    import inspect

    #Append dummy data
    name_of_test = inspect.stack()[0][3]
    logHours.currentTime=str(time.time()).split('.')[0]
    logHours.readableTime = time.strftime('(%Y-%m-%d %H:%M:%S)', time.localtime(float(logHours.currentTime)))
    sample_text = name_of_test + ' pyTest at: ' + str(logHours.currentTime)+ '  ' + logHours.readableTime + "\n"

    logHours.initializeInternalVariables()
    p = Path(logHours.files['allTaskChanges'])
    #os.remove(p)
    Path.unlink(p)
    p.write_text(sample_text)
    expected = [sample_text]

    logHours.readInAllChanges()
    actual = logHours.lineList
    assert actual == expected

def test_setFolderPath(logHours):
    #Setup
    import time
    day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    logHours.initializeInternalVariables()

    #Run setFolderPath
    #should have been done in initializeInternalVariables(): logHours.setFolderPath()

    #Examine the results
    assert logHours.files['15minSummary'].upper() == os.path.normpath('C:/Users/' + os.getlogin() + '/LogHours/' + day + '/15minuteSummary.log').upper()
    assert logHours.files['allTaskChanges'].upper() == os.path.normpath('C:/users/' + os.getlogin() + '/LogHours/' + day + '/allTaskChanges.log').upper()
    assert logHours.files['Hours'].upper() == os.path.normpath('C:/Users/' + os.getlogin() + '/LogHours/hours.log').upper()
    assert logHours.files['Summary'].upper() == os.path.normpath('C:/Users/' + os.getlogin() + '/LogHours/' + day + '/dailySummary.log').upper()
    assert logHours.files['Temp'].upper() == os.path.normpath('C:/Users/' + os.getlogin() + '/LogHours/temp').upper()
    #assert logHours.files['Latest'].upper() == os.path.normpath('C:/users/' + os.getlogin() + '/LogHours/latest.log').upper()

@pytest.mark.skip(reason="incomplete")
def test_summarizeToday():
    pass

@pytest.mark.skip(reason="incomplete")
def test_updateDict(logHours):
    pass

@pytest.mark.skip(reason="incomplete")
def test_writeLatestValuesToTempFile(logHours):
    pass
    
@pytest.mark.skip(reason="incomplete")
def test_writeTodaysSummaryToFile():
    pass

