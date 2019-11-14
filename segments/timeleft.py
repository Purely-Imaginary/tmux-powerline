import subprocess, time, datetime

def cmdline(command):
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process.communicate()[0]


def getUptimeDict():
    # uptimeData = subprocess.run(["tuptime", "-tcs"], stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
    # uptimeData = subprocess.check_output(["tuptime -tcs"], shell=True).decode('utf-8')
    uptimeData = cmdline(["tuptime", "-tcs"]).decode('utf-8').split("\n")
    # print(uptimeData,end="|")
    uptimeParsedData = {}
    for entry in uptimeData:
        parsedEntry = entry.split(",")
        if parsedEntry[0][1:-1] == "No." or parsedEntry[0] == "":
            continue
        startDate = time.strftime('%Y-%m-%d', time.localtime(int(parsedEntry[1][1:-1])))
        seconds = int(parsedEntry[2][1:-4])

        if startDate not in uptimeParsedData:
            uptimeParsedData[startDate] = 0

        uptimeParsedData[startDate] = uptimeParsedData[startDate] + seconds
    
    return uptimeParsedData

def getDatesForPastDays(numberOfDays):
    oneDay = datetime.timedelta(days=1)
    currentDate = datetime.datetime.now().date() - oneDay # without today
    pastDays = []
    for i in range (numberOfDays-1):
        pastDays.append(currentDate.isoformat()) 
        currentDate -= oneDay
    return pastDays

def getDates():
    weekday = datetime.datetime.isoweekday(datetime.datetime.now())
    dayOfMonth = datetime.datetime.now().day

    return {
        "month": getDatesForPastDays(dayOfMonth),
        "week": getDatesForPastDays(weekday)
        }

def calculateSeconds(dates, uptimeDict):
    result = 0
    for date in dates:
        if date in uptimeDict:
            result += uptimeDict[date] - 28800 # 8 hours

    return result

def formatTime(timeString):
    returnString = "";
    if timeString[:1] == "-":
        returnString = "-"
        timeString = timeString[1:]

    x=datetime.timedelta(seconds=int(timeString))
    return returnString + str(x)[:-3]

def todayGoTime(uptimeDict):
    secondsLeft = calculateSeconds([datetime.datetime.now().date().isoformat()],uptimeDict) * -1
    return (datetime.datetime.now() + datetime.timedelta(seconds=secondsLeft)).strftime('%H:%M')

def main():
    uptimeData = getUptimeDict()
    dates = getDates()
    returnString = ""
    returnString += "M:" + formatTime(str(calculateSeconds(dates['month'],uptimeData)))
    returnString += " W:" + formatTime(str(calculateSeconds(dates['week'],uptimeData)))
    returnString += " D:" + formatTime(str(calculateSeconds([datetime.datetime.now().date().isoformat()],uptimeData)))

    returnString += " " + todayGoTime(uptimeData)
    print(returnString, end="")
    return returnString
    # print(uptimeData)

main()
