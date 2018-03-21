from datetime import timedelta, datetime

from agenda.month import Month
from agenda.weekday import Weekday
import re

class Activity:
    _price_finder = re.compile('Prijs:\s*(€(\d+,\d{2}|\d+)/€(\d+,\d{2}|\d+))')
    _price_splitter = re.compile('€(\d+,\d{2}|\d+)/€(\d+,\d{2}|\d+)')

    def __init__(self, begin_time, end_time, begin_date, end_date, name, description, location, price="€0/€3"):
        # Catch faulty user behavior, 00:00 is no longer the same day
        if end_time == "00:00":
            end_time = "23:59"
            end_date -= timedelta(days=1)

        self.begin_time = begin_time
        self.end_time = end_time
        self.begin_date = begin_date
        self.end_date = end_date
        self.name = name
        self._description = ""
        self.price = price
        self.description = description
        self.location = location

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        m = self._price_finder.search(description)
        if m:
            description = self._price_finder.sub("", description)
            member, non_member = self._price_splitter.search(m.group()).groups()
            self.price = "€{}/€{}".format(member, non_member)
        self._description = description

    def get_day_name(self):
        return Weekday(self.begin_date.weekday()).name

    def get_month_name(self):
        return Month(self.begin_date.month).name

    def is_multi_day(self) -> bool:
        if (self.end_date - self.begin_date).days > 0:
            return True
        return False

    def draw(self, day: int, week: int, month: int):
        pass

    def __str__(self):
        return "{} {} - {} {}\n{}: {}\n{}\n{}".format(self.begin_date,
                                                      self.begin_time,
                                                      self.end_date,
                                                      self.end_time,
                                                      self.name,
                                                      self.description,
                                                      self.location,
                                                      self.price)

    def __repr__(self):
        return "<Activity {} {}>".format(self.name, self.begin_date)

    def __lt__(self, other):

        my_datetime = datetime(self.begin_date.year,
                               self.begin_date.month,
                               self.begin_date.day,
                               int(self.begin_time.split(":")[0]),
                               int(self.begin_time.split(":")[1]))
        other_datetime = datetime(other.begin_date.year,
                                  other.begin_date.month,
                                  other.begin_date.day,
                                  int(other.begin_time.split(":")[0]),
                                  int(other.begin_time.split(":")[1]))
        return my_datetime < other_datetime
