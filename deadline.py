from datetime import datetime, timedelta
from config import CONFIG
import babel.dates
import dateparser
import pytz

class Deadline:
    time: datetime
    comment: str

    def __init__(self, time: datetime, comment: str):
        self.time = time
        self.comment = comment

    @staticmethod
    def parse(s: str):
        """Parse a Deadline in the format "time;comment"."""
        tokens = s.split(";", 1)
        if (len(tokens) < 2):
            raise ValueError("Please format your deadline in the form date;comment (e.g. '4 June 2019; Math Homework 5').")

        dt = dateparser.parse(tokens[0].strip(),
                              settings = CONFIG["parser_settings"])
        if dt == None:
            raise ValueError("Can't read date '{}'.".format(tokens[0]))
        return Deadline(dt, tokens[1].strip())


    def format_time(self):
        dt = self.time
        if (dt.hour, dt.minute, dt.second) == (0,0,0):
            return babel.dates.format_date(dt.date(),
                                           format="short",
                                           locale=CONFIG["locale"])
        else:
            return babel.dates.format_datetime(dt,
                                               format="short",
                                               locale=CONFIG["locale"])


    def __str__(self):
        return "{} ({})".format(self.comment, self.format_time())


    def in_how_many_days(self):
        """checks if a deadline is expired; i.e. more than a day old"""
        localtime = pytz.timezone(CONFIG["timezone"])
        now = pytz.utc.localize(datetime.utcnow(), is_dst=None).astimezone(localtime)
        return (self.time.date() - now.date()).days

    def friendly_date(self):
        localtime = pytz.timezone(CONFIG["timezone"])
        days = self.in_how_many_days()
        if days == 0:
            return "Today"
        elif days == -1:
            return "Yesterday"
        elif days == 1:
            return "Tomorrow"

        # calculate number of weeks between now and the date
        start_of_deadline_week = self.time.date() - timedelta(days=self.time.weekday())
        now = pytz.utc.localize(datetime.utcnow(), is_dst=None).astimezone(localtime)
        start_of_this_week = now.date() - timedelta(days=now.weekday())
        weeks = (start_of_deadline_week - start_of_this_week).days // 7

        if weeks < -1:
            return "{} weeks ago".format(-weeks)
        elif weeks == -1:
            return self.time.strftime("Last %A, %d %b %y")
        elif weeks == 0:
            return self.time.strftime("This %A, %d %b %y")
        elif weeks == 1:
            return self.time.strftime("Next %A, %d %b %y")
        else:
            return "In {} weeks".format(weeks)
