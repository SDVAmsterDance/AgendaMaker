import math
from textwrap import wrap

from PIL import Image, ImageDraw
import style
from utils.activity import Activity
from utils.activity_type import ActivityType
from utils.google_calendar import get_events
from utils.weekday import Weekday
import utils.text as text
import datetime


class DrawAgenda:
    scale = 2

    width = 877
    height = 620
    header_height = 90
    weekdays_height = 60
    font_size = 25
    calendar_start_y = header_height + weekdays_height
    debug = False

    def __init__(self):
        self.width *= self.scale
        self.height *= self.scale
        self.header_height *= self.scale
        self.weekdays_height *= self.scale
        self.font_size *= self.scale
        self.calendar_start_y = self.header_height + self.weekdays_height

        self.im = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.im)

    def make_agenda_image(self):
        self.draw_header()
        self.draw_squiggles()
        self.draw_weekdays()
        start_date, end_date = self.draw_month()
        now = datetime.datetime.now()
        self.draw_activities(month=now.month, start_date=start_date, end_date=end_date)
        if self.debug:
            self.draw_debug()

    def draw_agenda(self):
        self.make_agenda_image()
        # self.im.thumbnail((self.width/self.scale, self.height/self.scale), Image.BICUBIC)
        self.im.save('test.gif', "GIF")

    def draw_header(self):
        margin_left = self.scale * 10
        banner_height = self.scale * 80
        banner_width = self.scale * 500
        header_text = "AmsterDance"
        now = datetime.datetime.now()
        month_text = now.strftime("%B %Y")
        print(month_text)

        self.draw.line([margin_left, self.header_height, self.width - (self.scale * 220), self.header_height],
                       fill=style.color['black'])

        self.draw.text(
            xy=[self.width - (self.scale * 210), (self.scale * 2) + self.header_height - style.font(size=self.font_size).getsize(month_text)[1]],
            text=month_text,
            fill=style.color['black'],
            font=style.font(size=self.font_size))

        self.draw.polygon([(margin_left, self.header_height - 1),
                           (margin_left, self.header_height - banner_height),
                           (margin_left + banner_width, self.header_height - banner_height),
                           (margin_left + banner_width - (self.scale * 40), self.header_height - (self.scale * 1))
                           ],
                          fill=style.color['red'])

        text_y0 = self.header_height - banner_height - (self.scale * 13)
        text.small_caps(self.draw,
                        (margin_left + (self.scale * 10), text_y0),
                        header_text,
                        font=style.font(size=banner_height),
                        fill=style.color["white"]
                        )

    def draw_month(self):
        now = datetime.datetime.now()
        day = 1
        month = now.month
        year = now.year
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
        margin = (self.scale * 45)
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
        text_y0 = ((y0 + y1) / 2) - (self.scale * 16)

        self.draw.text((text_x0, text_y0), str(date.day), font=style.font(size=self.font_size),
                       fill=style.color["white"])

    def draw_squiggles(self):
        for i, day in enumerate(Weekday):
            x0 = (i * (self.width / 7))
            x1 = ((i + 1) * (self.width / 7))

            # self.draw.line([(x0, 0), (x0, self.height)], fill=style.color['lblack'], width=3)
            text_x0 = ((x0 + x1) / 2)
            self.draw.line([(text_x0, self.calendar_start_y), (text_x0, self.height - (self.scale * 50))], fill=style.color["black"])

    def draw_weekdays(self):
        weekdays_text_y = self.header_height + (self.scale * 10)
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
        internal_events_calendarIDs = ['p68brdnv6bp4q8qu0g8o1gv914@group.calendar.google.com']
        external_events_calendarIDs = ['k37nshvnqob4c484497713cboc@group.calendar.google.com']
        for calendarID in internal_events_calendarIDs:
            self.draw_calendar_activities(calendarID, month, start_date, end_date, activity_type=ActivityType.INTERN)

        for calendarID in external_events_calendarIDs:
            self.draw_calendar_activities(calendarID, month, start_date, end_date, activity_type=ActivityType.EXTERN)

    def draw_calendar_activities(self, calendarID, month, start_date, end_date,
                                 activity_type: ActivityType = ActivityType.INTERN):
        events = get_events(calendarId=calendarID, start_date=start_date,
                            end_date=end_date)
        for event in events:
            days = (event.begin_date - start_date).days
            if activity_type is ActivityType.INTERN:
                self.draw_internal_activity(days % 7, int(math.floor(days / 7)), month, event)
            else:
                self.draw_external_activity(days % 7, int(math.floor(days / 7)), month, event)

    def draw_internal_activity(self, day: int, week: int, month: int, activity: Activity) -> None:
        margin = self.scale * 40
        y_min = self.scale * 10
        x_min = self.scale * 20
        x_max = self.scale * 35
        row_height = (self.height - self.calendar_start_y) / 6
        x0 = (day * (self.width / 7)) + margin
        x1 = ((day + 1) * (self.width / 7)) - margin
        block_width = x1 - x0
        y0 = self.calendar_start_y + week * row_height
        y1 = y0 + block_width

        background = style.color['black']
        title_color = style.color['white']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['red']
        if activity.begin_date.month != month:
            background = style.color['lblack']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        # black card
        self.draw.polygon([(x0 - x_min, y0 - y_min),
                           (x1 + x_max, y0 - y_min),
                           (x1 + x_min, y1 + y_min),
                           (x0 - x_max, y1 + y_min)],
                          fill=background)

        font = style.font(size=self.scale * 16)
        spacing = self.scale * -2
        y = y0 - y_min
        title = text.wrap(string=activity.name, font=font, width=(x1 + x_min) - (x0 - x_min))

        self.draw.multiline_text((x0 - x_min, y), title, font=font, fill=title_color, spacing=spacing)
        y += 2 * (self.scale * 14)  # 14 because that seems to be the line height
        font = style.font(size=self.scale * 13)
        self.draw.text((x0 - x_min, y), "{}-{}".format(activity.begin_time, activity.end_time), font=font,
                       fill=text_color)
        y += font.getsize("{}-{}".format(activity.begin_time, activity.end_time))[1]
        self.draw.text((x0 - x_min, y), activity.location, font=font, fill=text_color)
        y += font.getsize(activity.location)[1]
        self.draw.text((x0 - x_min, y), activity.price, font=font, fill=text_color)

        # red date
        card_height = (y1 + y_min) - (y0 - y_min)
        slope_width = x_max - x_min
        date_width = self.scale * 14
        self.draw.polygon([(x1 + x_max - date_width, y0 - y_min),
                           (x1 + x_max, y0 - y_min),
                           (x1 + x_max - date_width / (card_height / slope_width), y0 - y_min + date_width),
                           (x1 + x_max - date_width, y0 - y_min + date_width)],
                          fill=date_background_color)

        text_x0 = text.vertical_center_text(str(activity.begin_date.day), font,
                                            x_min=x1 + x_max - date_width, x_max=x1 + x_max - (self.scale * 3))

        self.draw.text((text_x0, y0 - y_min),
                       str(activity.begin_date.day),
                       font=font,
                       fill=date_text_color)

    def draw_external_activity(self, day: int, week: int, month: int, activity: Activity) -> None:
        margin = self.scale * 40
        y_min = self.scale * 10
        x_min = self.scale * 20
        x_max = self.scale * 35
        row_height = (self.height - self.calendar_start_y) / 6
        x0 = (day * (self.width / 7)) + margin
        x1 = ((day + 1) * (self.width / 7)) - margin
        block_width = x1 - x0
        y0 = self.calendar_start_y + week * row_height
        y1 = y0 + block_width
        card_horizontal_middle = (y1 + y0) / 2
        half_card_height = card_horizontal_middle - (y0 - y_min)

        background = style.color['dred']
        title_color = style.color['lred']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['white']
        if activity.begin_date.month != month:
            background = style.color['lblack']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        # hexagon
        # print(x0, x1, y0, y1, x_min, x_max, y_min, (y0 - y1) / 2)
        self.draw.polygon([(x0 - x_max, card_horizontal_middle),
                           (x0 - x_min, y0 - y_min),
                           (x1 + x_min, y0 - y_min),
                           (x1 + x_max, card_horizontal_middle),
                           (x1 + x_min, y1 + y_min),
                           (x0 - x_min, y1 + y_min)],
                          fill=background)

        font = style.font(size=self.scale * 16)
        spacing = self.scale * -2
        y = y0 - y_min
        title = text.wrap(string=activity.name, font=font, width=(x1 + x_min) - (x0 - x_min))

        self.draw.multiline_text((x0 - x_min, y), title, font=font, fill=title_color, spacing=spacing)
        y += 2 * self.scale * 14  # 14 because that seems to be the line height
        font = style.font(size=self.scale * 13)
        self.draw.text((x0 - x_min, y), "{}-{}".format(activity.begin_time, activity.end_time), font=font,
                       fill=text_color)
        y += font.getsize("{}-{}".format(activity.begin_time, activity.end_time))[1]
        self.draw.text((x0 - x_min, y), activity.location, font=font, fill=text_color)
        y += font.getsize(activity.location)[1]
        self.draw.text((x0 - x_min, y), activity.price, font=font, fill=text_color)

        # red date
        slope_width = x_max - x_min
        half_date_height = font.getsize(str(activity.begin_date.day))[1] / 2
        intersect = (half_date_height/half_card_height)*slope_width
        self.draw.polygon([(x1 + x_min, card_horizontal_middle - half_date_height),
                           (x1 + x_max - intersect, card_horizontal_middle - half_date_height),
                           (x1 + x_max, card_horizontal_middle),
                           (x1 + x_max - intersect, card_horizontal_middle + half_date_height),
                           (x1 + x_min, card_horizontal_middle + half_date_height)],
                          fill=date_background_color)

        text_x0 = text.vertical_center_text(str(activity.begin_date.day), font,
                                            x_min=x1 + x_min, x_max=x1 + x_max-(self.scale * 3))

        self.draw.text((text_x0, card_horizontal_middle - half_date_height - (self.scale * 1)),
                       str(activity.begin_date.day),
                       font=font,
                       fill=date_text_color)

    def draw_debug(self):
        # header
        self.draw.rectangle([0, 0, self.width, self.header_height], outline="green")

        # weekdays
        self.draw.rectangle([0, self.header_height + 1, self.width, self.header_height + self.weekdays_height],
                            outline="blue")

        # calendar
        self.draw.rectangle([0, self.calendar_start_y + 1, self.width, self.height], outline="red")
