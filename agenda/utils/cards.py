from agenda.activity.activity import Activity
from agenda.utils import style as st

from agenda.utils.shapes import *

import numpy as np


class Card(object):
    def __init__(self, style=st.AgendaStyle()):
        self.style = style

    def _draw_all_dates(self, start, date, draw, width, y0, y1, background_color, text_color, font,
                        date_shape_function):
        # Draw date boxes on every day of the event
        start_day = start[0]
        dates = [str(dat) for dat in np.arange(int(date[0]), int(date[1]) + 1, 1)]
        margin = self.style.scale * 40
        for i, date in enumerate(dates):
            x = ((start_day + 1 + i) * (width / 7)) - margin
            date_shape_function(draw, date, x, y0, y1, background_color, text_color, font)

    def _draw_multi_day_details(self, draw, activity: Activity, font, text_color, spacing, x0, x1, y):
        print("run?")
        start_time = "{}-...".format(activity.begin_time)
        end_time = "...-{}".format(activity.end_time)

        # Draw the details in the event box
        # draw.multiline_text((x0 - shape.x_min(), y), start_time, font=font, fill=text_color, spacing=spacing)
        # draw.multiline_text((x1 - shape.x_min(), y), end_time, font=font, fill=text_color, spacing=spacing)
        if activity.location:
            y += (self.style.scale * 10)
            # draw.multiline_text((x0 - shape.x_min(), y), activity.location, font=font, fill=text_color, spacing=spacing)
        y += (self.style.scale * 10)
        # draw.multiline_text((x0 - shape.x_min(), y), activity.price, font=font, fill=text_color, spacing=spacing)

    def card(self, draw: ImageDraw = None, x0: Union[int, float] = 0, x1: Union[int, float] = 0,
             y0: Union[int, float] = 0, y1: Union[int, float] = 0, background_color: Tuple[int, int, int] = (0, 0, 0),
             date_background_color: Tuple[int, int, int] = (0, 0, 0), text_color: Tuple[int, int, int] = (0, 0, 0),
             title_color: Tuple[int, int, int] = (0, 0, 0), date_text_color: Tuple[int, int, int] = (0, 0, 0),
             title: str = "", date: tuple = (), activity: Activity = None, shape: Shape = Shape(), **kwargs):
        """
        :param draw:
        :param x0:
        :param x1:
        :param y0:
        :param y1:
        :param background_color:
        :param date_background_color:
        :param text_color:
        :param title_color:
        :param date_text_color:
        :param title:
        :param date:
        :param start:
        :param width:
        :param activity: the event to draw
        :param shape: a list of points (x, y) to draw a polygon
        :param date_function: function reference that draws the dates
        """
        # print("Unused stuff: {}".format(kwargs))

        draw.polygon(shape.get_shape(), fill=background_color)
        # print(shape.get_scaled_height(), shape.x_max(), shape.x_min())
        # print(shape.get_scaled_height(), self.style.X_MAX, self.style.X_MIN)
        # print()

        title_font_size = int(shape.get_scaled_height()/(5.3/self.style.scale))
        font = self.style.font(size=title_font_size)

        spacing = self.style.scale * -title_font_size/8
        y = y0 - shape.y_min()
        title = text.wrap(string=title, font=font, width=(x1 + shape.x_min()) - (x0 - shape.x_min()))

        draw.multiline_text((x0 - shape.x_min(), y), title, font=font, fill=title_color, spacing=spacing)

        details_font_size = int(shape.get_scaled_height()/(7/self.style.scale))
        # print(shape.get_scaled_height(), shape.get_height(), 2 * title_font_size + 3 * details_font_size)
        font = self.style.font(size=details_font_size)

        y += 2 * font.size

        # Single day vs multi day events
        if self.style.style_type == 'flyer' or date[0] == date[1]:
            # Draw date box
            # shape.draw_date()
            shape.draw_date(draw, date[0], date_background_color, date_text_color, font)

            # date_function(draw, date[0], x1, y0, y1, date_background_color, date_text_color, font)
            if activity.location:
                details = "{}-{}\n{}\n{}".format(activity.begin_time, activity.end_time, activity.location,
                                                 activity.price)
            else:
                details = "{}-{}\n{}".format(activity.begin_time, activity.end_time, activity.price)
            # Draw event details
            draw.multiline_text((x0 - shape.x_min(), y), details, font=font, fill=text_color, spacing=spacing)
        else:
            # print(style.style_type, date)
            # Draw date boxes on every day of the event
            # _draw_all_dates(start, date, draw, width, y0, y1, date_background_color, date_text_color, font,
            #                 date_function)
            self._draw_multi_day_details(draw, activity, font, text_color, spacing, x0, x1, y)

    def internal_card(self, x1, x0, y1, y0, cut='', style=st.Style(), **kwargs) -> None:
        shape = Paralellogram(x0=x0, x1=x1, y0=y0, y1=y1, style=style).set_cut(cut)
        self.card(shape=shape, x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)
        return shape

    def external_card(self, x1, x0, y1, y0, cut='', style=st.Style(), **kwargs):
        shape = Hexagon(x0=x0, x1=x1, y0=y0, y1=y1, style=style).set_cut(cut)
        self.card(shape=shape, x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)
        return shape
