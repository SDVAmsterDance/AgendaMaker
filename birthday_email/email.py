import datetime
from apis.google_sheets import batch_get_sheet_values
from jinja2 import Template, Environment

# TEMPLATE_ENVIRONMENT = Environment(keep_trailing_newline=True)

class Email(object):
    def __init__(self, birthdays, template=""):
        self.birthdays = birthdays
        self.template = template

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

    def make_email(self, month):
        birthdays = self._get_birthdays(month)
        template = Template(self.template)
        # template = TEMPLATE_ENVIRONMENT.from_string(self.template)
        return template.render(birthdays=birthdays)


