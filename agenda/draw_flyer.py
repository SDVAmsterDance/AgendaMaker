import datetime
import math
from typing import Tuple

from PIL import Image, ImageDraw
from collections import defaultdict

import agenda.utils.text as text
from agenda.activity.activity import Activity
from agenda.activity_type import ActivityType
from agenda.utils import style, shapes
from agenda.weekday import Weekday
from apis.google_calendar import get_events
from calendar import monthrange


class DrawFlyer:
    width = 833
    height = 1179
    header_height = 90
    weekdays_height = 60
    font_size = 25
    calendar_start_y = header_height + weekdays_height
    debug = False

    def __init__(self, month, year, internal_activities, external_activities):
        self.width *= style.scale
        self.height *= style.scale
        self.header_height *= style.scale
        self.weekdays_height *= style.scale
        self.font_size *= style.scale
        self.calendar_start_y = self.header_height + self.weekdays_height

        self.month = month
        self.year = year
        self.internal_activities = internal_activities
        self.external_activities = external_activities

        self.im = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.im)

    def _make_agenda_image(self):
        self.draw_header()
        self.draw_squiggles()
        start_date = datetime.date(self.year, self.month, 1)
        end_date = datetime.date(self.year, self.month, monthrange(2012, 2)[1] - 1)
        self.draw_activities(start_date=start_date, end_date=end_date)
        if self.debug:
            self.draw_debug()

    def draw_agenda(self):
        self._make_agenda_image()
        # self.im.thumbnail((self.width/style.scale, self.height/style.scale), Image.BICUBIC)
        date = datetime.date(self.year, self.month, 1)
        month_text = date.strftime("%B%Y")
        fname = '{}.png'.format(month_text)
        self.im.save(fname, "png")
        return fname

    def draw_header(self):
        margin_left = style.scale * 10
        banner_height = style.scale * 80
        banner_width = style.scale * 500
        header_text = "AmsterDance"

        date = datetime.date(self.year, self.month, 1)
        month_text = date.strftime("%B %Y")

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
                           (margin_left + banner_width - (style.scale * 40),
                            self.header_height - (style.scale * 1))
                           ],
                          fill=style.color['red'])

        text_y0 = self.header_height - banner_height - (style.scale * 13)
        text.small_caps(self.draw,
                        (margin_left + (style.scale * 10), text_y0),
                        header_text,
                        font=style.font(size=banner_height),
                        fill=style.color["white"]
                        )

    def draw_squiggles(self):
        self.draw.line([(self.width / 2, self.calendar_start_y), (self.width / 2, self.height - (style.scale * 50))],
                       fill=style.color["black"])

    def draw_activities(self, start_date, end_date):
        internal_events_calendarIDs = self.internal_activities
        external_events_calendarIDs = self.external_activities
        activity_list = []
        for calendarID in internal_events_calendarIDs:
            if calendarID:
                activity_list += [(event, ActivityType.INTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]

        for calendarID in external_events_calendarIDs:
            if calendarID:
                activity_list += [(event, ActivityType.EXTERN) for event in get_events(calendarId=calendarID,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date)]
        self.draw_flyer_activities(sorted(activity_list))

    def draw_calendar_activities(self, calendarID, start_date, end_date,
                                 activity_type: ActivityType = ActivityType.INTERN):
        events = get_events(calendarId=calendarID, start_date=start_date,
                            end_date=end_date)
        for event in events:
            if activity_type is ActivityType.INTERN:
                self.draw_internal_activity(activity=event)
            else:
                self.draw_external_activity(activity=event)

    def draw_flyer_activities(self, activity_list):

        for i, (event, activity_type) in enumerate(activity_list):
            print(i, event, activity_type)
            if activity_type is ActivityType.INTERN:
                self.draw_internal_activity(activity=event, activity_index=i, num_activities=len(activity_list))
            else:
                self.draw_external_activity(activity=event, activity_index=i, num_activities=len(activity_list))

    def draw_activity(self, activity: Activity = None,
                      card_style: dict = defaultdict(lambda: (0, 0, 0)),
                      activity_shape: callable = None,
                      activity_index=0,
                      num_activities=1):
        background_color = card_style['background_color']
        title_color = card_style['title_color']
        date_text_color = card_style['date_text_color']
        date_background_color = card_style['date_background_color']
        text_color = card_style['text_color']

        params = {
            "draw": self.draw,
            "background_color": background_color,
            "date_background_color": date_background_color,
            "text_color": text_color,
            "title_color": title_color,
            "date_text_color": date_text_color,
            "title": activity.name,
            "date": (str(activity.begin_date.day), str(activity.end_date.day)),
            "activity": activity,
            "width": self.width
        }

        x0, x1, y0, y1 = self.calculate_card_size(margin=style.scale * 40, activity_index=activity_index, num_activities=num_activities)
        activity_shape(x0=x0, x1=x1, y0=y0, y1=y1, **params)

    def draw_internal_activity(self, activity: Activity, activity_index: int, num_activities:int) -> None:
        background_color = style.color['black']
        title_color = style.color['white']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['red']
        if activity.begin_date.month != self.month:
            background_color = style.color['lblack']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        card_style = {'background_color': background_color,
                      'title_color': title_color,
                      'date_background_color': date_background_color,
                      'text_color': text_color,
                      'date_text_color': date_text_color}
        self.draw_activity(activity, card_style, shapes.internal_card, activity_index=activity_index, num_activities=num_activities)

    def draw_external_activity(self, activity: Activity, activity_index: int, num_activities:int) -> None:
        background_color = style.color['dred']
        title_color = style.color['lred']
        date_text_color = style.color['white']
        date_background_color = style.color['red']
        text_color = style.color['white']
        if activity.begin_date.month != self.month:
            background_color = style.color['ldred']
            title_color = style.color['lwhite']
            date_background_color = style.color['lred']
            text_color = style.color['lred']

        card_style = {'background_color': background_color,
                      'title_color': title_color,
                      'date_background_color': date_background_color,
                      'text_color': text_color,
                      'date_text_color': date_text_color}
        self.draw_activity(activity, card_style, shapes.external_card, activity_index=activity_index, num_activities=num_activities)

    def calculate_card_size(self, activity_index, num_activities, margin):
        card_width = 700
        row_height = (self.height - self.calendar_start_y) / num_activities

        x0 = (self.width / 2) - (card_width / 2)
        x1 = (self.width / 2) + (card_width / 2)

        y0 = self.calendar_start_y + activity_index * row_height
        y1 = y0 + row_height - margin
        return x0, x1, y0, y1

    def draw_debug(self):
        # header
        self.draw.rectangle([0, 0, self.width, self.header_height], outline="green")

        # weekdays
        self.draw.rectangle([0, self.header_height + 1, self.width, self.header_height + self.weekdays_height],
                            outline="blue")

        # calendar
        self.draw.rectangle([0, self.calendar_start_y + 1, self.width, self.height], outline="red")
