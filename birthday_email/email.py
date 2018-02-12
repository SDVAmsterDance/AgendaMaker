import datetime
from calendar import monthrange

from agenda.activity_type import ActivityType
from apis.google_calendar import get_events
from apis.google_sheets import batch_get_sheet_values
from jinja2 import Template, Environment

# TEMPLATE_ENVIRONMENT = Environment(keep_trailing_newline=True)

class Email(object):
    def __init__(self, birthdays, internal_activities, external_activities, template=""):
        self.birthdays = birthdays
        self.template = template
        self.internal_activities = internal_activities
        self.external_activities = external_activities

    def _get_birthdays(self, month):
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
                                              {'name': name, 'birthdate': birthdate.strftime("%d %B"), 'age': age}))

        return sorted(birthdays, key=lambda l: l[0])

    def _get_events(self, start_date, end_date):
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

    def make_email(self, month, year):
        birthdays = self._get_birthdays(month)

        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, monthrange(2012, 2)[1] - 1)

        events = self._get_events(start_date, end_date)
        template = Template(self.template)
        # template = TEMPLATE_ENVIRONMENT.from_string(self.template)
        return template.render(birthdays=birthdays, events=events)


