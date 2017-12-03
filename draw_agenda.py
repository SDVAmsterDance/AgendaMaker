import math
from textwrap import wrap

from PIL import Image, ImageDraw
import style
from utils.activity import Activity
from utils.google_calendar import get_events
from utils.weekday import Weekday
import utils.text as text
import datetime


class DrawAgenda:
    width = 877
    height = 620
    header_height = 90
    weekdays_height = 60
    font_size = 25
    calendar_start_y = header_height + weekdays_height
    debug = False

    def __init__(self):
        self.im = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.im)

    def make_agenda_image(self):
        self.draw_header()
        self.draw_squiggles()
        self.draw_weekdays()
        start_date, end_date = self.draw_month()
        self.draw_activities(month=11, start_date=start_date, end_date=end_date)
        if self.debug:
            self.draw_debug()

    def draw_agenda(self):
        self.make_agenda_image()
        self.im.save('test.gif', "GIF")

    def draw_header(self):
        margin_left = 10
        banner_height = 80
        banner_width = 500
        header_text = "AmsterDance"
        month_text = "November 2017"

        self.draw.line([margin_left, self.header_height, self.width - 220, self.header_height],
                       fill=style.color['black'])

        self.draw.text(
            xy=[self.width - 210, 2 + self.header_height - style.font(size=self.font_size).getsize(month_text)[1]],
            text=month_text,
            fill=style.color['black'],
            font=style.font(size=self.font_size))

        self.draw.polygon([(margin_left, self.header_height - 1),
                           (margin_left, self.header_height - banner_height),
                           (margin_left + banner_width, self.header_height - banner_height),
                           (margin_left + banner_width - 40, self.header_height - 1)
                           ],
                          fill=style.color['red'])

        text_y0 = self.header_height - banner_height - 13
        text.small_caps(self.draw,
                        (margin_left + 10, text_y0),
                        header_text,
                        font=style.font(size=banner_height),
                        fill=style.color["white"]
                        )

    def draw_month(self):
        day = 1
        month = 11
        year = 2017
        date = datetime.date(year, month, day)

        if date.weekday():
            date = date - datetime.timedelta(days=date.weekday())
        else:
            date = date - datetime.timedelta(days=7)
        start_date = date

        for w in range(6):
            for d in range(7):
                self.draw_day(d, w, date, month)
                date += datetime.timedelta(days=1)
        end_date = date - datetime.timedelta(days=1)
        return start_date, end_date

    def draw_day(self, d, w, date, month):
        margin = 45
        row_height = (self.height - self.calendar_start_y) / 6
        x0 = (d * (self.width / 7)) + margin
        x1 = ((d + 1) * (self.width / 7)) - margin
        block_width = x1 - x0
        y0 = self.calendar_start_y + w * row_height
        y1 = y0 + block_width

        color = style.color['red']
        if date.month != month:
            color = style.color['lred']
        self.draw.rectangle([x0, y0, x1, y1], fill=color)
        font = style.font(size=self.font_size)
        text_x0 = text.vertical_center_text(str(date.day), font, x_min=x0, x_max=x1)
        text_y0 = ((y0 + y1) / 2) - 16

        self.draw.text((text_x0, text_y0), str(date.day), font=style.font(size=self.font_size),
                       fill=style.color["white"])

    def draw_squiggles(self):
        for i, day in enumerate(Weekday):
            x0 = (i * (self.width / 7))
            x1 = ((i + 1) * (self.width / 7))

            # self.draw.line([(x0, 0), (x0, self.height)], fill=style.color['lblack'], width=3)
            text_x0 = ((x0 + x1) / 2)
            self.draw.line([(text_x0, self.calendar_start_y), (text_x0, self.height - 50)], fill=style.color["black"])

    def draw_weekdays(self):
        weekdays_text_y = self.header_height + 10
        font = style.font(size=self.font_size)
        for i, day in enumerate(Weekday):
            x0 = (i * (self.width / 7))
            x1 = ((i + 1) * (self.width / 7))

            # self.draw.line([(x0, 0), (x0, self.height)], fill=style.color['lwhite'], width=3)
            text_w, _ = self.draw.textsize(day.name, font=font)
            text_x0 = text.vertical_center_text(day.name, font, x_min=x0, x_max=x1)
            self.draw.text((text_x0, weekdays_text_y), day.name, font=font,
                           fill=style.color["black"])

    def draw_activities(self, month, start_date, end_date):
        events = get_events(calendarId='sfeablf370g74009oau35jte18@group.calendar.google.com', start_date=start_date,
                            end_date=end_date)
        for event in events:
            days = (event.begin_date - start_date).days
            self.draw_activity(days % 7, int(math.floor(days / 7)), month, event)

    def draw_activity(self, day: int, week: int, month: int, activity: Activity) -> None:
        margin = 40
        y_min = 10
        x_min = 20
        x_max = 35
        row_height = (self.height - self.calendar_start_y) / 6
        x0 = (day * (self.width / 7)) + margin
        x1 = ((day + 1) * (self.width / 7)) - margin
        block_width = x1 - x0
        y0 = self.calendar_start_y + week * row_height
        y1 = y0 + block_width

        black = style.color['black']
        white = style.color['white']
        red = style.color['red']
        if activity.begin_date.month != month:
            black = style.color['lblack']
            white = style.color['lwhite']
            red = style.color['lred']

        # black card
        self.draw.polygon([(x0 - x_min, y0 - y_min),
                           (x1 + x_max, y0 - y_min),
                           (x1 + x_min, y1 + y_min),
                           (x0 - x_max, y1 + y_min)],
                          fill=black)

        font = style.font(size=16)
        spacing = -2
        y = y0 - y_min
        title = text.wrap(string=activity.name, font=font, width=(x1 + x_min)-(x0 - x_min))

        self.draw.multiline_text((x0 - x_min, y), title, font=font, fill=white, spacing=spacing)
        y += 2 * 14  # 14 because that seems to be the line height
        font = style.font(size=13)
        self.draw.text((x0 - x_min, y), "{}-{}".format(activity.begin_time, activity.end_time), font=font,
                       fill=red)
        y += font.getsize("{}-{}".format(activity.begin_time, activity.end_time))[1]
        self.draw.text((x0 - x_min, y), activity.location, font=font, fill=red)
        y += font.getsize(activity.location)[1]
        self.draw.text((x0 - x_min, y), activity.price, font=font, fill=red)

        # red date
        card_height = (y1 + y_min) - (y0 - y_min)
        slope_width = x_max - x_min
        date_width = 14
        self.draw.polygon([(x1 + x_max - date_width, y0 - y_min),
                           (x1 + x_max, y0 - y_min),
                           (x1 + x_max - date_width / (card_height / slope_width), y0 - y_min + date_width),
                           (x1 + x_max - date_width, y0 - y_min + date_width)],
                          fill=red)

        text_x0 = text.vertical_center_text(str(activity.begin_date.day), font,
                                            x_min=x1 + x_max - date_width, x_max=x1 + x_max - 3)

        self.draw.text((text_x0, y0 - y_min),
                       str(activity.begin_date.day),
                       font=font,
                       fill=white)

    def draw_debug(self):
        # header
        self.draw.rectangle([0, 0, self.width, self.header_height], outline="green")

        # weekdays
        self.draw.rectangle([0, self.header_height + 1, self.width, self.header_height + self.weekdays_height],
                            outline="blue")

        # calendar
        self.draw.rectangle([0, self.calendar_start_y + 1, self.width, self.height], outline="red")
