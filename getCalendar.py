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
eventIDs = []
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
eventID = 0
for event in events:
    eventID = eventID + 1
    if type(event['DTSTART'].dt) is datetime.datetime:

        dtStart = event['DTSTART'].dt.astimezone(toZone)
        dtEnd = event['DTEND'].dt.astimezone(toZone)
        name = event["SUMMARY"]
        date = dtStart.date()

        minute = str(dtStart.minute)
        if str(dtStart.minute) == "0":
            minute = "00"
        elif dtStart.minute < 10:
            minute = "0" + str(dtStart.minute)
        startMinute = int(minute)
        startHour = int(dtStart.hour)
        if startHour > 12:
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
        if endHour > 12:
            end = str(dtEnd.hour - 12) + ":" + minute + " pm"
        else:
            end = str(dtEnd.hour) + ":" + minute + " am"

        details = event["DESCRIPTION"]
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

        eventIDs.append(eventID)
        eventNames.append(name)
        eventDates.append(date)
        eventStartTimes.append(start)
        eventEndTimes.append(end)
        eventDetails.append(details)
        eventAllDays.append(isAllDay)
        eventDayOfWeeks.append(dayOfWeek)
        eventStartHours.append(startHour)
        eventStartMinutes.append(startMinute)
        eventEndHours.append(endHour)
        eventEndMinutes.append(endMinute)

    else:
        name = event["SUMMARY"]
        date = event["DTSTART"].dt
        start = None
        end = None
        startMinute = None
        startHour = None
        details = event["DESCRIPTION"]
        isAllDay = True
        dw = str(event['DTSTART'].dt.weekday())

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

        eventIDs.append(eventID)
        eventNames.append(name)
        eventDates.append(date)
        eventStartTimes.append(start)
        eventEndTimes.append(end)
        eventDetails.append(details)
        eventAllDays.append(isAllDay)
        eventDayOfWeeks.append(dayOfWeek)
        eventStartHours.append(startHour)
        eventStartMinutes.append(startMinute)
        eventEndHours.append(endHour)
        eventEndMinutes.append(endMinute)

# Now we put the results into a data frame
# Put results into DataFrame
df = pd.DataFrame({"id": eventIDs, "eventDate": eventDates, "eventStartTime": eventStartTimes, "eventEndTime": eventEndTimes, "eventName": eventNames, "eventDetails": eventDetails, "eventIsAllDay": eventAllDays, "eventDayOfWeek": eventDayOfWeeks,"eventStartHour": eventStartHours,"eventStartMinute": eventStartMinutes,"eventEndHour": eventEndHours,"eventEndMinute": eventEndMinutes})

# Connect to the MSSQL Server
engine = create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
print("Writing Calendar entries to SQL Server")
df.to_sql(name='calendarEvents', con=engine, if_exists='replace', index=False)

print("Done")

# Next we get the non-recurring events for the current day
# if 1 == 1:
#     for event in googleCal.walk('VEVENT'):
#         if type(event['DTSTART'].dt) is datetime:
#             if event['DTSTART'].dt.date() == today.date():
#                 print(event['SUMMARY'])
#                 # print(component.get('dtstart'))
#                 # print(component.get('dtend'))
#                 # print(component.get('dtstamp'))
#                 print(event['DTSTART'].dt)
#         elif event['DTSTART'].dt == today.date():
#             print("Outlier")
#             print(event['SUMMARY'])
#             print(event['DTSTART'].dt)












    # if component.name == "VEVENT":
    #     print(component.get('summary'))
    #     print(component.get('dtstart'))
    #     print(component.get('dtend'))
    #     print(component.get('dtstamp'))
        # print(component.get('dtstart'))
        # print(component.get('dtend'))
        # print(component.get('dtstamp'))

#print(g)


#c = Calendar(urllib.urlopen(url).read().decode())
#c = Calendar(urlopen(url).read().decode())

#import re

#text =  c
#print(re.search("SUMMARY:.*?:", text, re.DOTALL).group())
#print(re.search("DESCRIPTION:.*?:", text, re.DOTALL).group())
#print(re.search("DTSTAMP:.*:?", text, re.DOTALL).group())
#print(re.search("SUMMARY"))
