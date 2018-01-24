import datetime
import math
from typing import Tuple

from PIL import Image, ImageDraw

import agenda.utils.text as text
from agenda.activity.activity import Activity
from agenda.activity_type import ActivityType
from agenda.utils import style, shapes
from agenda.weekday import Weekday
from apis.google_calendar import get_events


class DrawAgenda:
    width = 877
    height = 620
    header_height = 90
    weekdays_height = 60
    font_size = 25
    calendar_start_y = header_height + weekdays_height
    debug = False

    def __init__(self):
        self.width *= style.scale
        self.height *= style.scale
        self.header_height *= style.scale
        self.weekdays_height *= style.scale
        self.font_size *= style.scale
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
        # self.im.thumbnail((self.width/style.scale, self.height/style.scale), Image.BICUBIC)
        self.im.save('test.gif', "GIF")

    def draw_header(self):
        margin_left = style.scale * 10
        banner_height = style.scale * 80
        banner_width = style.scale * 500
        header_text = "AmsterDance"
        now = datetime.datetime.now()
        month_text = now.strftime("%B %Y")
        print(month_text)

        self.draw.line([margin_left, self.header_height, self.width - (style.scale * 220), self.header_height],
                       fill=style.color['black'])

        self.draw.text(
            xy=[self.width - (style.scale * 210),
                (style.scale * 2) + self.header_height - style.font(size=self.font_size).getsize(month_text)[1]],
            text=month_text,
            fill=style.color['black'],
            font=style.font(size=self.font_size))

        self.draw.polygon([(margin_left, self.header_height - 1),
                           (margin_left, self.header_height - banner_height),
                           (margin_left + banner_width, self.header_height - banner_height),
                           (margin_left + banner_width - (style.scale * 40), self.header_height - (style.scale * 1))
                           ],
                          fill=style.color['red'])

        text_y0 = self.header_height - banner_height - (style.scale * 13)
        text.small_caps(self.draw,
                        (margin_left + (style.scale * 10), text_y0),
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
        margin = (style.scale * 45)
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
        text_y0 = ((y0 + y1) / 2) - (style.scale * 16)

        self.draw.text((text_x0, text_y0), str(date.day), font=style.font(size=self.font_size),
                       fill=style.color["white"])

    def draw_squiggles(self):
        for i, day in enumerate(Weekday):
            x0 = (i * (self.width / 7))
            x1 = ((i + 1) * (self.width / 7))

            text_x0 = ((x0 + x1) / 2)
            self.draw.line([(text_x0, self.calendar_start_y), (text_x0, self.height - (style.scale * 50))],
                           fill=style.color["black"])

    def draw_weekdays(self):
        weekdays_text_y = self.header_height + (style.scale * 10)
        font = style.font(size=self.font_size)
        for i, day in enumerate(Weekday):
            x0 = (i * (self.width / 7))
            x1 = ((i + 1) * (self.width / 7))

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
            if event.is_multi_day():
                start_day = (event.begin_date - start_date).days
                end_day = (event.end_date - start_date).days
                start_weekday_num = start_day % 7
                end_weekday_num = end_day % 7
                start_week = int(math.floor(start_day / 7))
                end_week = int(math.floor(end_day / 7))
                if activity_type is ActivityType.INTERN:
                    self.draw_internal_activity(start=(start_weekday_num, start_week), end=(end_weekday_num, end_week),
                                                month=month, activity=event)
                else:
                    self.draw_external_activity(start=(start_weekday_num, start_week), end=(end_weekday_num, end_week),
                                                month=month, activity=event)

            else:
                day = (event.begin_date - start_date).days
                weekday_num = day % 7
                week = int(math.floor(day / 7))
                if activity_type is ActivityType.INTERN:
                    self.draw_internal_activity(start=(weekday_num, week), month=month, activity=event)
                else:
                    self.draw_external_activity(start=(weekday_num, week), month=month, activity=event)

    def draw_internal_activity(self, start: Tuple[int, int], month: int, activity: Activity,
                               end: Tuple[int, int] = None) -> None:
        start_day, start_week = start
        x0, x1, y0, y1 = self.calculate_card_size((start_day, start_week), margin=style.scale * 40)

        if end:
            end_day, end_week = end
            if end_week == start_week:
                x0, x1, y0, y1 = self.calculate_card_size(start=(start_day, start_week), end=(end_day, end_week),
                                                          margin=style.scale * 40)
                pass
            else:
                # multiple weeks, harder
                pass

        background_color = style.color['black']
        title_color = style.color['white']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['red']
        if activity.begin_date.month != month:
            background_color = style.color['lblack']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        details = "{}-{}\n{}".format(activity.begin_time, activity.end_time, activity.price)
        shapes.internal_card(self.draw, x0, x1, y0, y1,
                             background_color, date_background_color, text_color, title_color, date_text_color,
                             title=activity.name, date=str(activity.begin_date.day), details=details)

    def draw_external_activity(self, start: Tuple[int, int], month: int, activity: Activity,
                               end: Tuple[int, int] = None) -> None:
        start_day, start_week = start
        x0, x1, y0, y1 = self.calculate_card_size((start_day, start_week), margin=style.scale * 40)
        if end:
            print(activity.name)
            end_day, end_week = end
            if end_week == start_week:
                x0, x1, y0, y1 = self.calculate_card_size(start=(start_day, start_week), end=(end_day, end_week),
                                                          margin=style.scale * 40)
                pass
            else:
                # multiple weeks, harder
                pass

        background_color = style.color['dred']
        title_color = style.color['lred']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['white']
        if activity.begin_date.month != month:
            background_color = style.color['lblack']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        details = "{}-{}\n{}".format(activity.begin_time, activity.end_time, activity.price)
        shapes.external_card(self.draw, x0, x1, y0, y1,
                             background_color, date_background_color, text_color, title_color, date_text_color,
                             title=activity.name, date=str(activity.begin_date.day), details=details)

    def calculate_card_size(self, start, margin, end=None):
        start_day, start_week = start
        row_height = (self.height - self.calendar_start_y) / 6
        x0 = (start_day * (self.width / 7)) + margin
        x1 = ((start_day + 1) * (self.width / 7)) - margin
        block_width = x1 - x0
        if end:
            end_day, end_week = end
            x1 = (end_day * (self.width / 7)) - margin
        y0 = self.calendar_start_y + start_week * row_height
        y1 = y0 + block_width
        return x0, x1, y0, y1

    def draw_debug(self):
        # header
        self.draw.rectangle([0, 0, self.width, self.header_height], outline="green")

        # weekdays
        self.draw.rectangle([0, self.header_height + 1, self.width, self.header_height + self.weekdays_height],
                            outline="blue")

        # calendar
        self.draw.rectangle([0, self.calendar_start_y + 1, self.width, self.height], outline="red")
