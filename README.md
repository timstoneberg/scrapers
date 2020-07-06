# Scrapers

These rudimentary scripts are used to scrape data from various internet sources for use in the CME Business Analytics Lab, at Loyola University Chicago.

## Getting Started

The current implementation simply runs these scripts at various times as a cron job.  You can also run them from the command line.

### Prerequisites

You need several Python packages installed to use these scrapers.

```
dotenv
bs4
urllib
pyodbc
pandas
time
alpha_vantage
sqlalchemy
re
datetime
urllib
pytz
recurring_ical_events
dateutil
shutil
contextLib
urllib2
```

## Executing

Simply run any script from the command line.

```
python getCalendar.py
```

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/documentation/) - The programming IDE used.
* [ChromeDriver](https://chromedriver.chromium.org/) - Used for website scraping.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/timstoneberg/scrapers/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Timmy Stoneberg** - *Initial work* - [Loyola University Chicago](https://github.com/timstoneberg)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* None at this time

