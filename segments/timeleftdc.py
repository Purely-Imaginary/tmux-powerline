import bs4
import datetime
import requests
from bs4 import BeautifulSoup as bs

# noinspection PyCallByClass
today = datetime.date.isoformat(datetime.datetime.now())


def timeToSeconds(time):
    return int(time[-2:]) + int(time[3:5]) * 60 + int(time[:2]) * 3600


def formatTimedelta(td):
    if td < datetime.timedelta(0):
        return '-' + formatTimedelta(-td)
    else:
        # Change this to format positive timedeltas the way you want
        return str(td)


def getDataFromWebsite():
    session = requests.session()

    cookieRequestUrl = 'http://192.168.1.201/'

    testRequest = session.get(url=cookieRequestUrl)
    cookieSessionID = testRequest.cookies['SessionID']

    checkRequestUrl = 'http://192.168.1.201/csl/check'
    checkRequestParams = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': 'SessionID=' + cookieSessionID}
    checkRequestBody = 'username=13&userpwd=12345'
    session.post(url=checkRequestUrl, data=checkRequestBody, headers=checkRequestParams)

    reportRequestUrl = 'http://192.168.1.201/csl/query?action=run&uid=17&sdate=2019-12-05&edate=2030-10-05'

    reportRequest = session.get(url=reportRequestUrl, headers=checkRequestParams)
    return reportRequest.content.decode()


def parseData(inputData):
    rawData = inputData.replace("\n", '').replace('  ', '').replace('\t', '')
    bsData = bs(rawData, features="html.parser")
    parsedData = {}
    for entry in bsData.table:
        if isinstance(entry, bs4.element.NavigableString) or 'NameTime' in entry.text:
            continue
        date = entry.contents[0].text
        time = entry.contents[3].text
        status = entry.contents[4].text
        if date not in parsedData:
            parsedData[date] = {
                'data': [],
                'secondsRequired': 28800,
                'secondsWorked': 0,
                'timeDifferenceInS': 0,
                'timeDifferenceInM': 0
            }
        parsedData[date]['data'].append([time, status])
    if parsedData['2019-12-10']['data'].__len__() == 1:
        parsedData['2019-12-10']['data'].append(['15:55:00', 'OUT'])
    return parsedData


def calculate(parsedData):
    _secondsLeft = 0
    for day in parsedData:
        if parsedData[day]['data'].__len__() < 2 or day == today:
            continue

        prevEntry = parsedData[day]['data'][0][0]

        for key, entry in enumerate(parsedData[day]['data']):
            if entry[0] == prevEntry:
                continue

            parsedData[day]['secondsWorked'] += (timeToSeconds(entry[0]) - timeToSeconds(prevEntry))
            if key < parsedData[day]['data'].__len__() - 1:
                prevEntry = parsedData[day]['data'][key + 1][0]

        parsedData[day]['timeDifferenceInS'] = parsedData[day]['secondsRequired'] - parsedData[day]['secondsWorked']
        parsedData[day]['timeDifferenceInM'] = round(parsedData[day]['timeDifferenceInS'] / 60, 2)
        _secondsLeft += parsedData[day]['timeDifferenceInS']

    return _secondsLeft, parsedData


secondsLeft, calcedData = calculate(parseData(getDataFromWebsite()))
todayStartTime = calcedData[today]['data'][0][0]
todayRequiredTime = calcedData[today]['secondsRequired'] + secondsLeft
getOutAt = str(datetime.timedelta(seconds=timeToSeconds(todayStartTime) + todayRequiredTime))

timeleft = formatTimedelta(datetime.timedelta(seconds=(timeToSeconds(todayStartTime) + todayRequiredTime) -
                                          timeToSeconds(str(datetime.datetime.now().time())[:8])))
print(getOutAt + " - " + timeleft)
