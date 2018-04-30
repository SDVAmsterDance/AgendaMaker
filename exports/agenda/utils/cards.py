from typing import Union

import numpy as np
from exports.agenda.activity.activity import Activity
from exports.agenda.utils import style as st
from exports.agenda.utils.shapes import *


class Card(object):
    def __init__(self, style=st.AgendaStyle()):
        self.style = style

    def _draw_all_dates(self, start, date, draw, background_color, text_color, font,
                        shape):
        # Draw date boxes on every day of the event
        dates = [str(dat) for dat in np.arange(int(date[0]), int(date[1]) + 1, 1)]
        margin = self.style.scale * self.style.margin
        width = shape.x1 - shape.x0
        card_width = (width - (2 + len(dates))*margin)/4
        for i, date in enumerate(dates[:-1]):
            x = start + margin + (i * (card_width + 2*margin))
            shape.draw_date(draw, date, background_color, text_color, font, x=x)

    def _draw_multi_day_details(self, draw, activity: Activity, font, text_color, spacing, x0, x1, y, shape):
        print("run?")
        start_time = "{}-...".format(activity.begin_time)
        end_time = "...-{}".format(activity.end_time)

        # Draw the details in the event box
        draw.multiline_text((x0 - shape.x_min(), y), start_time, font=font, fill=text_color, spacing=spacing)
        draw.multiline_text((x1 - shape.x_min(), y), end_time, font=font, fill=text_color, spacing=spacing)
        if activity.location:
            y += (self.style.scale * 10)
            draw.multiline_text((x0 - shape.x_min(), y), activity.location, font=font, fill=text_color, spacing=spacing)
        y += (self.style.scale * 10)
        draw.multiline_text((x0 - shape.x_min(), y), activity.price, font=font, fill=text_color, spacing=spacing)

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
        :param activity:
        :param shape:
        :param kwargs:
        :return:
        """

        draw.polygon(shape.get_shape(), fill=background_color)

        title_font_size = int(shape.get_scaled_height()/(5.3/self.style.scale))
        font = self.style.font(size=title_font_size)

        spacing = self.style.scale * -title_font_size/8
        y = y0 - shape.y_min()
        title = text.wrap(string=title, font=font, width=(x1 + shape.x_min()) - (x0 - shape.x_min()))

        draw.multiline_text((x0 - shape.x_min(), y), title, font=font, fill=title_color, spacing=spacing)

        details_font_size = int(shape.get_scaled_height()/(7/self.style.scale))
        font = self.style.font(size=details_font_size)

        y += 2 * font.size
        # Single day vs multi day events
        if self.style.style_type == 'flyer' or date[0] == date[1]:
            # Draw date box
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
            # Draw date boxes on every day of the event

            self._draw_all_dates(x0, date, draw, date_background_color, date_text_color, font, shape=shape)
            # self._draw_all_dates(dates=date, draw=draw, background_color=date_background_color,
            #                      text_color=date_text_color, font=font, shape=shape)
            self._draw_multi_day_details(draw, activity, font, text_color, spacing, x0, x1, y,  shape)

    def internal_card(self, x1, x0, y1, y0, cut='', style=st.Style(), **kwargs) -> None:
        shape = Paralellogram(x0=x0, x1=x1, y0=y0, y1=y1, style=style).set_cut(cut)
        self.card(shape=shape, x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)
        return shape

    def external_card(self, x1, x0, y1, y0, cut='', style=st.Style(), **kwargs):
        shape = Hexagon(x0=x0, x1=x1, y0=y0, y1=y1, style=style).set_cut(cut)
        self.card(shape=shape, x0=x0, x1=x1, y0=y0, y1=y1, **kwargs)
        return shape
