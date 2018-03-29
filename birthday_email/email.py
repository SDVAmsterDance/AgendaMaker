import datetime
from calendar import monthrange

from agenda.activity_type import ActivityType
from agenda.month import Maand, Month
from apis.google_calendar import get_events
from apis.google_sheets import batch_get_sheet_values
from jinja2 import Template, Environment

# TEMPLATE_ENVIRONMENT = Environment(keep_trailing_newline=True)

class Email(object):
    def __init__(self, birthdays, internal_activities, external_activities, internal_activities_en, external_activities_en, template=""):
        self.birthdays = birthdays
        self.template = template
        self.internal_activities = internal_activities
        self.external_activities = external_activities
        self.internal_activities_en = internal_activities_en
        self.external_activities_en = external_activities_en

    def _get_birthdays(self, month):
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
        now = datetime.datetime.now()
        year = now.year
        range_names = [
            "Allertijden!A2:C",
            "Allertijden!G2:G",
            "Allertijden!R2:R"
        ]
        zero_date = datetime.date(1899, 12, 30)
        birthdays = []
        for spreadsheet_id in self.birthdays:
            values, service = batch_get_sheet_values(spreadsheet_id, range_names, valueRenderOption="UNFORMATTED_VALUE")
            if values:
                for name, lid, birthdate in values:
                    name = " ".join(filter(None, name))
                    lid = lid[0]
                    if lid == "Ja" and birthdate:
                        birthdate = zero_date + datetime.timedelta(days=int(birthdate[0]))
                        age = year - birthdate.year
                        if birthdate.month == month:

                            birthdays.append((datetime.date(year, birthdate.month, birthdate.day),
                                              {'name': name,
                                               'verjaardag': "{} {}".format(birthdate.day, Maand(birthdate.month).name),
                                               'birthdate': "{} of {}".format(ordinal(birthdate.day), Month(birthdate.month).name),
                                               'age': age}))

        return sorted(birthdays, key=lambda l: l[0])

    def _get_nl_events(self, start_date, end_date):
        activity_list = []
        for calendarID in self.internal_activities:
            if calendarID:
                activity_list += [(event, ActivityType.INTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]

        for calendarID in self.external_activities:
            if calendarID:
                activity_list += [(event, ActivityType.EXTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]
        return sorted(activity_list)

    def _get_en_events(self, start_date, end_date):
        activity_list = []
        for calendarID in self.internal_activities_en:
            if calendarID:
                activity_list += [(event, ActivityType.INTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]

        for calendarID in self.external_activities_en:
            if calendarID:
                activity_list += [(event, ActivityType.EXTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]
        return sorted(activity_list)

    def make_email(self, month, year):
        birthdays = self._get_birthdays(month)

        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, monthrange(2012, 2)[1] - 1)

        nl_events = self._get_nl_events(start_date, end_date)
        en_events = self._get_en_events(start_date, end_date)
        template = Template(self.template)
        # template = TEMPLATE_ENVIRONMENT.from_string(self.template)
        return template.render(birthdays=birthdays, nl_events=nl_events, en_events=en_events)


