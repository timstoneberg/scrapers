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
eventEndTimes = []
eventNames = []
eventDetails = []
eventAllDays = []

# Setup the localized time
utc=pytz.UTC
tdy = datetime.datetime.now()
tmw = tdy + datetime.timedelta(days=1)
today = utc.localize(tdy)
tomorrow = utc.localize(tmw)


# Begin getting the recurring events for the current day
startDate = (today.year, today.month, today.day)
endDate = (tomorrow.year, tomorrow.month, tomorrow.day)
events = recurring_ical_events.of(googleCal).between(startDate, endDate)

eventID = 0
for event in events:
    eventID = eventID + 1
    if type(event['DTSTART'].dt) is datetime.datetime:
        name = event["SUMMARY"]
        date = event["DTSTART"].dt.date()

        minute = str(event["DTSTART"].dt.minute)
        if str(event["DTSTART"].dt.minute) == "0":
            minute = "00"
        elif event["DTSTART"].dt.minute < 10:
            minute = "0" + str(event["DTSTART"].dt.minute)
        start = str(event["DTSTART"].dt.hour) + ":" + minute

        minute = str(event["DTEND"].dt.minute)
        if str(event["DTEND"].dt.minute) == "0":
            minute = "00"
        elif event["DTEND"].dt.minute < 10:
            minute = "0" + str(event["DTEND"].dt.minute)
        end = str(event["DTEND"].dt.hour) + ":" + minute

        details = event["DESCRIPTION"]
        isAllDay = False

        eventIDs.append(eventID)
        eventNames.append(name)
        eventDates.append(date)
        eventStartTimes.append(start)
        eventEndTimes.append(end)
        eventDetails.append(details)
        eventAllDays.append(isAllDay)

    else:
        name = event["SUMMARY"]
        date = event["DTSTART"].dt
        start = None
        end = None
        details = event["DESCRIPTION"]
        isAllDay = True

        eventIDs.append(eventID)
        eventNames.append(name)
        eventDates.append(date)
        eventStartTimes.append(start)
        eventEndTimes.append(end)
        eventDetails.append(details)
        eventAllDays.append(isAllDay)

# Now we put the results into a data frame
# Put results into DataFrame
df = pd.DataFrame({"id": eventIDs, "eventDate": eventDates, "eventStartTime": eventStartTimes, "eventEndTime": eventEndTimes, "eventName": eventNames, "eventDetails": eventDetails, "eventIsAllDay": eventAllDays})

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
