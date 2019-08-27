# Lets me store	passwords in .env file
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

# Setup the Finviz Scraper
activeNYSENames = []
activeNYSEPrices = []
activeNYSEPercentChanges = []
activeNYSETotalVolumes = []
activeNYSEURL = "https://finviz.com/screener.ashx?v=111&s=ta_mostactive&f=exch_nyse"

activeNASDAQNames = []
activeNASDAQPrices = []
activeNASDAQPercentChanges = []
activeNASDAQTotalVolumes = []
activeNASDAQURL = "https://finviz.com/screener.ashx?v=111&s=ta_mostactive&f=exch_nasd"

# Scrape Finviz for NYSE
r = requests.get(activeNYSEURL)
data = r.text
soup = BeautifulSoup(data, features='lxml')

print("Grabbing NYSE Most Active")
for listing in soup.find_all('tr', attrs={'class': re.compile('table\-(?:(?!\-row\-cp)(?:.|\n))*\-row\-cp')}):
    i = 0
    for name in listing.find_all('a', attrs={'class': 'screener-link'}):
        item = name.get_text()
        item = item.replace(',', '')

        if(i == 1):
            item = item[:25]
            activeNYSENames.append(item)
        if(i == 7):
            activeNYSEPrices.append(item)
        if(i == 8):
            item = item.replace('%', '')
            activeNYSEPercentChanges.append(item)
        if(i == 9):
            activeNYSETotalVolumes.append(item)
        i = i + 1

# Scrape Finviz for NASDAQ
r = requests.get(activeNASDAQURL)
data = r.text
soup = BeautifulSoup(data, features='lxml')

print("Grabbing NASDAQ Most Active")
timestamp = str(time.ctime(int(time.time())))
for listing in soup.find_all('tr', attrs={'class': re.compile('table\-(?:(?!\-row\-cp)(?:.|\n))*\-row\-cp')}):
    i = 0
    for name in listing.find_all('a', attrs={'class': 'screener-link'}):
        item = name.get_text()
        item = item.replace(',', '')

        if(i == 1):
            item = item[:25]
            activeNASDAQNames.append(item)
        if(i == 7):
            activeNASDAQPrices.append(item)
        if(i == 8):
            item = item.replace('%', '')
            activeNASDAQPercentChanges.append(item)
        if(i == 9):
            activeNASDAQTotalVolumes.append(item)
        i = i + 1

# Put results into DataFrame
activesNYSE = pd.DataFrame({"name": activeNYSENames, "close": activeNYSEPrices, "pchange": activeNYSEPercentChanges, "volume": activeNYSETotalVolumes, "timestamp": timestamp})
activesNASDAQ = pd.DataFrame({"name": activeNASDAQNames, "close": activeNASDAQPrices, "pchange": activeNASDAQPercentChanges, "volume": activeNASDAQTotalVolumes, "timestamp": timestamp})

# Connect to the MSSQL Server
engine = create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
print("Writing NYSE most actives to SQL Server")
activesNYSE.to_sql(name='actives_nyse', con=engine, if_exists='replace', index=False)
print("Writing NASDAQ most actives to SQL Server")
activesNASDAQ.to_sql(name='actives_nasdaq', con=engine, if_exists='replace', index=False)

print("Done")
