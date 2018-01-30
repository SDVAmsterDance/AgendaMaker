import datetime
from apis.google_sheets import batch_get_sheet_values

class Email(object):

    def __init__(self, birthdays):
        self.birthdays = birthdays

    def make_email(self, month):
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
                    name = " ".join(filter(None,name))
                    lid = lid[0]
                    if lid == "Ja" and birthdate:
                            birthdate = zero_date + datetime.timedelta(days=int(birthdate[0]))
                            age = year - birthdate.year
                            if birthdate.month == month:
                                birthdays.append((datetime.date(year, birthdate.month, birthdate.day),
                                                  [name, birthdate.strftime("%d %B"), age]))

                birthdays = sorted(birthdays, key=lambda l:l[0])

        for b, text in birthdays:
            print("{} is jarig op {} en wordt {} jaar oud!".format(text[0], text[1], text[2]))
