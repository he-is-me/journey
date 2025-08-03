from pathlib import Path
import calendar
import datetime



def test_calendar():
    print(calendar.monthrange(
        year=datetime.datetime.today().year,
        month=datetime.datetime.today().month)[1])
    print(calendar.Calendar().itermonthdays4(
        year=datetime.datetime.today().year,
        month=datetime.datetime.date()
