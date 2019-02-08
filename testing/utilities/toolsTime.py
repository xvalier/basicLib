import time

#TIMESTAMP FUNCTIONS------------------------------------------------------------
#Return a timestamp string
def createTimestamp():
    return time.strftime('%Y-%b-%d %I:%M:%S',time.localtime())

#Calculate time difference between two timestamps, return as string
def calculateTimeDiff(timestamp1, timestamp2):
    #Convert formatted time strings to integers in terms of seconds
    rawTime1 = time.mktime(time.strptime(timestamp1, '%Y-%b-%d %I:%M:%S'))
    rawTime2 = time.mktime(time.strptime(timestamp2, '%Y-%b-%d %I:%M:%S'))
    #Calulate and return difference in seconds
    timeDiff = rawTime2 -rawTime1
    return timeDiff

def createSessionID(token, timestamp):
    #Reformat timestamp into more condensed format
    rawTime       = time.strptime(timestamp, '%Y-%b-%d %I:%M:%S')
    condensedtime = time.strftime('%Y%m%d%I%M%S',rawTime)
    return token+condensedtime

#Un-tested class for timer debugging (work on later)
class timer:
    def __init__(self):
        self.start = 0
        self.end   = 0
    def tic():
        self.start = time.time()
    def toc():
        self.end   = time.time() + self.start
        return self.end
