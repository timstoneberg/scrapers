# Lets me store passwords in .env file
import os
from dotenv import load_dotenv
load_dotenv()

# To use:  os.getenv("VARIABLENAME")

import requests
from bs4 import BeautifulSoup
import re
import urllib
import pyodbc
import pandas as pd
import time
from alpha_vantage.timeseries import TimeSeries
from sqlalchemy import create_engine
from sqlalchemy import update

# Setup the CMELab MSSQL Database connection
params =   'DRIVER=' + os.getenv("SQLDRIVER") + ';'
params +=  'fast_executemany=True;'
params +=  'SERVER=' + os.getenv("SQLSERVER") + ';'
params +=  'PORT=' + os.getenv("SQLPORT") + ';'
params +=  'DATABASE=' + os.getenv("SQLDB") + ';'
params +=  'UID=' + os.getenv("SQLUID") + ';'
params +=  'PWD=' + os.getenv("SQLPASS") + ';'

params = urllib.quote_plus(params)

# Setup the Alphavantage API
apiKey = os.getenv("AVAPIKEY")
ts = TimeSeries(key=apiKey, output_format='pandas', indexing_type='date')

tickerList = {
    "AMZN":"Amazon.com, Inc.",
    "ATVI":"Activision Blizzard Inc.",
    "BA":"Boeing Co",
    "BAX":"Baxter International Inc",
    "BLK":"Blackrock Inc.",
    "BMY":"Bristol-Meyers Squibb Co.",
    "CELH":"Celsisus Holdings",
    "CL":"Colgate-Palmolive Company",
    "DIS":"Walt Disney Co",
    "EMB":"iShares J.P. Morgan USD Emerging Markets Bond ETF",
    "FMS":"Fresenius Medical Care AG & Co.",
    "GD":"General Dynamics Corporation",
    "GSK":"GlaxoSmithKline plc",
    "IAU":"iShares Gold Trust",
    "LAKE":"Lakeland Industries, Inc.",
    "LMT":"Lockheed Martin Corp.",
    "LUV":"Southwest Airlines",
    "MDR":"McDermott International Inc.",
    "MRK":"Merck & Co.",
    "MU":"Micron Technologies",
    "MUB":"iShares National Municipal Bond ETF",
    "NGG":"National Grid",
    "NLY":"Annaly Capital Management",
    "NOC":"Northtrop Grumman Corporation",
    "PANW":"Palo Alto Networks Inc.",
    "PXD":"Pioneer Natural Resources Co.",
    "PYPL":"PayPal Holdings",
    "RDS-A":"Royal Dutch Shell",
    "RTN":"Raytheon",
    "SHY":"iShares 1-3 Year Treasury Fund",
    "SNAP":"Snap",
    "SYY":"Sysco Corp.",
    "TLT":"iShares 20 Year Treasury Fund",
    "TSLA":"Tesla",
    "UTX":"United Technologies Corp.",
    "UUP":"Invesco DB U.S. Dollar Index Fund",
    "VIXY":"ProShares VIX Short-Term Futures Fund",
    "VZ":"Verizon Communications",
    "WDC":"Western Digital Corp.",
    "XOM":"Exxon Mobil"
}

# This is a temporary thing for testing
tickerList = {
    "DIS":"Walt Disney Co"
}

# Get the Alphavantage data
totalData = pd.DataFrame()
totalChangeData = pd.DataFrame()
timestamp = str(time.ctime(int(time.time())))

for stockTicker in tickerList:
    print("Fetching " + stockTicker + " from Alphavantage.com at " + str(time.ctime(int(time.time()))))
    stockName = tickerList[stockTicker]
    data, meta_data = ts.get_daily(symbol=stockTicker, outputsize='full')

    # Add index as new column to data frame
    data['date'] = data.index
    data['ticker'] = stockTicker
    data['name'] = stockName[:25]
    data['timestamp'] = timestamp

    totalData = totalData.append(data)

    # Create DataFrame for change data table
    c = data.head(3)["4. close"]
    d = data.head(3)["date"]
    yesterday = c[2]
    today = c[1]
    increase = today - yesterday
    pchange = increase / yesterday * 100
    increase = round(increase, 2)
    pchange = round(pchange, 2)

    change = [[d[1], stockTicker, increase, pchange]]
    changeData = pd.DataFrame(change, columns=['date', 'ticker', 'change', 'pchange'])

    totalChangeData = totalChangeData.append(changeData)
    time.sleep(15) # Needed for free version of Alphavantage due to limit of 5 data pulls per minute

print("Data pull from Alphavantage successful.  Writing to SQL Server now.")

# Connect to the MSSQL Server
engine = create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
print("Writing daily change data to SQL Server at " + str(time.ctime(int(time.time()))))
print("Fetching " + stockTicker + " from Alphavantage.com at " + str(time.ctime(int(time.time()))))
    
totalChangeData.to_sql(name='daily_change', con=engine, if_exists='replace', index=False)
print("Writing daily data to SQL Server at " + str(time.ctime(int(time.time()))))
totalData.to_sql(name='daily', con=engine, if_exists='replace', index=False)

print("Done")
