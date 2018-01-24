from datetime import timedelta


class Activity:
    def __init__(self, begin_time, end_time, begin_date, end_date, name, descriptor, location, price="€0/€3"):
        # Catch faulty user behavior, 00:00 is no longer the same day
        if end_time == "00:00":
            end_time = "23:59"
            end_date -= timedelta(days=1)

        self.begin_time = begin_time
        self.end_time = end_time
        self.begin_date = begin_date
        self.end_date = end_date
        self.name = name
        self.descriptor = descriptor
        self.location = location
        self.price = price

    def __str__(self):
        return "{} {} - {} {}\n{}: {}\n{}\n{}".format(self.begin_date,
                                                      self.begin_time,
                                                      self.end_date,
                                                      self.end_time,
                                                      self.name,
                                                      self.descriptor,
                                                      self.location,
                                                      self.price)

    def is_multi_day(self) -> bool:
        if (self.end_date - self.begin_date).days > 0:
            return True
        return False

    def draw(self, day: int, week: int, month: int):
        pass
