# Lets me store	passwords in .env file
import os
from dotenv import load_dotenv
load_dotenv()

from icalendar import Calendar, Event
import datetime
import urllib
import pytz
import recurring_ical_events
import pandas as pd
from sqlalchemy import create_engine
from dateutil import tz

# Setup the CMELab MSSQL Database connection
params =   'DRIVER=' + os.getenv("SQLDRIVER") + ';'
params +=  'fast_executemany=True;'
params +=  'SERVER=' + os.getenv("SQLSERVER") + ';'
params +=  'PORT=' + os.getenv("SQLPORT") + ';'
params +=  'DATABASE=RiseDisplay;'
params +=  'UID=' + os.getenv("SQLUID") + ';'
params +=  'PWD=' + os.getenv("SQLPASS") + ';'

params = urllib.quote_plus(params)

# Get the iCal file from Google
url = "https://calendar.google.com/calendar/ical/cmeanalyticslab%40gmail.com/public/basic.ics"
g = urllib.urlopen(url).read().decode('UTF-8')
googleCal=Calendar.from_ical(g)

# Setup variables to store the events of various types
eventUIDs = []
eventCustomUIDs = []
eventDates = []
eventStartTimes = []
eventStartHours = []
eventStartMinutes = []
eventEndTimes = []
eventEndHours = []
eventEndMinutes = []
eventNames = []
eventDetails = []
eventAllDays = []
eventDayOfWeeks = []

# Setup the localized time
utc=pytz.UTC
fromZone = tz.gettz('UTC')
toZone = tz.gettz('America/Chicago')
tdy = datetime.datetime.now()
tmw = tdy + datetime.timedelta(days=1)
mdy = tdy - datetime.timedelta(days=tdy.weekday())
sat = mdy + datetime.timedelta(days=6)

today = tdy
tomorrow = tmw
monday = mdy
saturday = sat

today = utc.localize(tdy)
tomorrow = utc.localize(tmw)
monday = utc.localize(mdy)
saturday = utc.localize(sat)

# Begin getting the recurring events for the current day
startDate = (today.year, today.month, today.day)
endDate = (tomorrow.year, tomorrow.month, tomorrow.day)

# Or we can get the recurring events for the current week
startDate = (monday.year, monday.month, monday.day)
endDate = (saturday.year, saturday.month, saturday.day)

events = recurring_ical_events.of(googleCal).between(startDate, endDate)

class MyCalEvent:
    def __init__(self):
        self.uid = None
        self.customUID = None
        self.name = None
        self.date = None
        self.start = None
        self.end = None
        self.details = None
        self.isAllDay = None
        self.dayOfWeek = None
        self.startMinute = None
        self.startHour = None
        self.endMinute = None
        self.endHour = None
        self.dw = None
        self.dayOfWeek = None

    def createTimedEvent(self, calEvent):
        dtStart = calEvent['DTSTART'].dt.astimezone(toZone)
        dtEnd = calEvent['DTEND'].dt.astimezone(toZone)
        name = calEvent["SUMMARY"]
        date = dtStart.date()

        minute = str(dtStart.minute)
        if str(dtStart.minute) == "0":
            minute = "00"
        elif dtStart.minute < 10:
            minute = "0" + str(dtStart.minute)

        startMinute = int(minute)
        startHour = int(dtStart.hour)

        if startHour >= 12:
            if startHour == 12:
                start = str(dtStart.hour) + ":" + minute + " pm"
            else:
                start = str(dtStart.hour - 12) + ":" + minute + " pm"
        else:
            start = str(dtStart.hour) + ":" + minute + " am"

        minute = str(dtEnd.minute)
        if str(dtEnd.minute) == "0":
            minute = "00"
        elif dtEnd.minute < 10:
            minute = "0" + str(dtEnd.minute)
        endMinute = int(minute)
        endHour = int(dtEnd.hour)

        if endHour >= 12:
            if endHour == 12:
                end = str(dtEnd.hour) + ":" + minute + " pm"
            else:
                end = str(dtEnd.hour - 12) + ":" + minute + " pm"
        else:
            end = str(dtEnd.hour) + ":" + minute + " am"

        details = calEvent["DESCRIPTION"]
        isAllDay = False
        dw = str(dtStart.weekday())

        # And some ugly if statements because python doesn't have switch()
        if dw == "0":
            dayOfWeek = "Monday"
        elif dw == "1":
            dayOfWeek = "Tuesday"
        elif dw == "2":
            dayOfWeek = "Wednesday"
        elif dw == "3":
            dayOfWeek = "Thursday"
        elif dw == "4":
            dayOfWeek = "Friday"
        elif dw == "5":
            dayOfWeek = "Saturday"
        elif dw == "6":
            dayOfWeek = "Sunday"
        else:
            dayOfWeek = None

        self.uid = calEvent['UID']
        self.name = name
        self.date = date
        self.customUID = str(self.uid) + str(self.date)
        self.start = start
        self.end = end
        self.details = details
        self.isAllDay = isAllDay
        self.dayOfWeek = dayOfWeek
        self.startMinute = startMinute
        self.startHour = startHour
        self.endMinute = endMinute
        self.endHour = endHour
        self.dw = dw
        self.dayOfWeek = dayOfWeek


    def createAllDayEvent(self, calEvent):
        self.name = calEvent["SUMMARY"]
        self.uid = calEvent['UID']
        self.date = calEvent["DTSTART"].dt
        self.customUID = str(self.uid) + str(self.date)
        self.start = None
        self.end = None
        self.startMinute = None
        self.startHour = None
        self.endMinute = None
        self.endHour = None
        self.details = calEvent["DESCRIPTION"]
        self.isAllDay = True
        self.dw = str(calEvent['DTSTART'].dt.weekday())

        if self.dw == "0":
            self.dayOfWeek = "Monday"
        elif self.dw == "1":
            self.dayOfWeek = "Tuesday"
        elif self.dw == "2":
            self.dayOfWeek = "Wednesday"
        elif self.dw == "3":
            self.dayOfWeek = "Thursday"
        elif self.dw == "4":
            self.dayOfWeek = "Friday"
        elif self.dw == "5":
            self.dayOfWeek = "Saturday"
        elif self.dw == "6":
            self.dayOfWeek = "Sunday"
        else:
            self.dayOfWeek = None


allEvents = {}


for event in events:
    newEvent = MyCalEvent()
    if type(event['DTSTART'].dt) is datetime.datetime:
        newEvent.createTimedEvent(event)
    else:
        newEvent.createAllDayEvent(event)

    allEvents[newEvent.customUID] = newEvent


# Next we get the non-recurring events for the current day
for event in googleCal.walk('VEVENT'):
    newEvent = MyCalEvent()

    if type(event['DTSTART'].dt) is datetime.date:
        eventDate = event['DTSTART'].dt
        testUID = str(event['UID']) + str(eventDate)

        if eventDate >= monday.date() and eventDate <= saturday.date():
            if testUID in allEvents:
                newEvent.createAllDayEvent(event)
                allEvents[newEvent.customUID] = newEvent
                print("Overwriting the existing event with modified item in a recurring event")
            else:
                newEvent.createAllDayEvent(event)
                allEvents[newEvent.customUID] = newEvent
                print("Adding a new single use event")
    else:
        eventDate = event['DTSTART'].dt.date()
        testUID = str(event['UID']) + str(eventDate)

        if eventDate >= monday.date() and eventDate <= saturday.date():
            if testUID in allEvents:
                newEvent.createTimedEvent(event)
                allEvents[newEvent.customUID] = newEvent
                print("Overwriting the existing event with modified item in a recurring event")
            else:
                newEvent.createTimedEvent(event)
                allEvents[newEvent.customUID] = newEvent
                print("Adding a new single use event")


# Iterate the dictionary to put values into array, because that's what pandas likes
for item in allEvents:
    eventUIDs.append(allEvents[item].uid)
    eventNames.append(allEvents[item].name)
    eventDates.append(allEvents[item].date)
    eventStartTimes.append(allEvents[item].start)
    eventEndTimes.append(allEvents[item].end)
    eventDetails.append(allEvents[item].details)
    eventAllDays.append(allEvents[item].isAllDay)
    eventDayOfWeeks.append(allEvents[item].dayOfWeek)
    eventStartHours.append(allEvents[item].startHour)
    eventStartMinutes.append(allEvents[item].startMinute)
    eventEndHours.append(allEvents[item].endHour)
    eventEndMinutes.append(allEvents[item].endMinute)
    eventCustomUIDs.append(allEvents[item].customUID)

# Now we put the results into a data frame
# Put results into DataFrame
df = pd.DataFrame({"uid": eventUIDs, "cuid": eventCustomUIDs, "eventDate": eventDates, "eventStartTime": eventStartTimes, "eventEndTime": eventEndTimes, "eventName": eventNames, "eventDetails": eventDetails, "eventIsAllDay": eventAllDays, "eventDayOfWeek": eventDayOfWeeks,"eventStartHour": eventStartHours,"eventStartMinute": eventStartMinutes,"eventEndHour": eventEndHours,"eventEndMinute": eventEndMinutes})

if df.empty:
    print("Exiting due to empty df dataframe.")
    exit()

# Connect to the MSSQL Server
engine = create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
print("Writing Calendar entries to SQL Server")
df.to_sql(name='GoogleCalendarEvents', con=engine, if_exists='replace', index=False)

print("Done")
