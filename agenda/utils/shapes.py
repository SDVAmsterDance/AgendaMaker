from typing import Tuple, Union, List

from PIL import ImageDraw, ImageFont

from agenda.activity.activity import Activity
from agenda.utils import style, text

import numpy as np

Y_MIN = style.scale * 10
X_MIN = style.scale * 20
X_MAX = style.scale * 35


def _draw_internal_date(draw: ImageDraw, date: str, x: Union[int, float], y0: Union[int, float],
                        y1: Union[int, float], background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                        font: ImageFont):
    """Draw the date on a specified position x on the event card."""
    card_height = (y1 + Y_MIN) - (y0 - Y_MIN)
    slope_width = X_MAX - X_MIN
    date_width = style.scale * 14
    draw.polygon([(x + X_MAX - date_width, y0 - Y_MIN),
                  (x + X_MAX, y0 - Y_MIN),
                  (x + X_MAX - date_width / (card_height / slope_width), y0 - Y_MIN + date_width),
                  (x + X_MAX - date_width, y0 - Y_MIN + date_width)],
                 fill=background_color)

    text_x0 = text.vertical_center_text(date, font,
                                        x_min=x + X_MAX - date_width, x_max=x + X_MAX - (style.scale * 3))

    draw.text((text_x0, y0 - Y_MIN),
              date,
              font=font,
              fill=text_color)


def _draw_external_date(draw: ImageDraw, date: str, x: Union[int, float], y0: Union[int, float],
                        y1: Union[int, float], background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                        font: ImageFont):
    """Draw the date on a specified position x on the event card."""
    card_horizontal_middle = (y1 + y0) / 2
    half_card_height = card_horizontal_middle - (y0 - Y_MIN)
    # red date
    slope_width = X_MAX - X_MIN
    half_date_height = font.getsize(date)[1] / 2
    intersect = (half_date_height / half_card_height) * slope_width
    draw.polygon([(x + X_MIN, card_horizontal_middle - half_date_height),
                  (x + X_MAX - intersect, card_horizontal_middle - half_date_height),
                  (x + X_MAX, card_horizontal_middle),
                  (x + X_MAX - intersect, card_horizontal_middle + half_date_height),
                  (x + X_MIN, card_horizontal_middle + half_date_height)],
                 fill=background_color)

    text_x0 = text.vertical_center_text(date, font,
                                        x_min=x + X_MIN, x_max=x + X_MAX - (style.scale * 3))

    draw.text((text_x0, card_horizontal_middle - half_date_height - (style.scale * 1)),
              date,
              font=font,
              fill=text_color)


def _draw_all_dates(start, date, draw, width, y0, y1, background_color, text_color, font, date_shape_function):
    # Draw date boxes on every day of the event
    start_day = start[0]
    dates = [str(dat) for dat in np.arange(int(date[0]), int(date[1]) + 1, 1)]
    margin = style.scale * 40
    for i, date in enumerate(dates):
        x = ((start_day + 1 + i) * (width / 7)) - margin
        date_shape_function(draw, date, x, y0, y1, background_color, text_color, font)


def _draw_multi_day_details(draw, activity: Activity, font, text_color, spacing, x0, x1, y):
    start_time = "{}-...".format(activity.begin_time)
    end_time = "...-{}".format(activity.end_time)

    # Draw the details in the event box
    draw.multiline_text((x0 - X_MIN, y), start_time, font=font, fill=text_color, spacing=spacing)
    draw.multiline_text((x1 - X_MIN, y), end_time, font=font, fill=text_color, spacing=spacing)
    if activity.location:
        y += (style.scale * 10)
        draw.multiline_text((x0 - X_MIN, y), activity.location, font=font, fill=text_color, spacing=spacing)
    y += (style.scale * 10)
    draw.multiline_text((x0 - X_MIN, y), activity.price, font=font, fill=text_color, spacing=spacing)


def card(draw: ImageDraw = None, x0: Union[int, float] = 0, x1: Union[int, float] = 0, y0: Union[int, float] = 0,
         y1: Union[int, float] = 0, background_color: Tuple[int, int, int] = (0, 0, 0),
         date_background_color: Tuple[int, int, int] = (0, 0, 0), text_color: Tuple[int, int, int] = (0, 0, 0),
         title_color: Tuple[int, int, int] = (0, 0, 0), date_text_color: Tuple[int, int, int] = (0, 0, 0),
         title: str = "", date: tuple = (), start: Tuple[int, int] = None,
         width: Union[int, float] = -1, activity: Activity=None, shape=List[Tuple], date_function=_draw_internal_date):
    # black card
    draw.polygon(shape,
                 fill=background_color)

    font = style.font(size=style.scale * 16)
    spacing = style.scale * -2
    y = y0 - Y_MIN
    title = text.wrap(string=title, font=font, width=(x1 + X_MIN) - (x0 - X_MIN))

    draw.multiline_text((x0 - X_MIN, y), title, font=font, fill=title_color, spacing=spacing)
    font = style.font(size=style.scale * 13)
    y += 2 * (style.scale * 14)  # 14 because that seems to be the line height

    # Single day vs multi day events
    if date[0] == date[1]:
        # Draw date box
        date_function(draw, date[0], x1, y0, y1, date_background_color, date_text_color, font)

        if activity.location:
            details = "{}-{}\n{}\n{}".format(activity.begin_time, activity.end_time, activity.location, activity.price)
        else:
            details = "{}-{}\n{}".format(activity.begin_time, activity.end_time, activity.price)
        # Draw event details
        draw.multiline_text((x0 - X_MIN, y), details, font=font, fill=text_color, spacing=spacing)
    else:
        # Draw date boxes on every day of the event
        _draw_all_dates(start, date, draw, width, y0, y1, date_background_color, date_text_color, font,
                        date_function)
        _draw_multi_day_details(draw, activity, font, text_color, spacing, x0, x1, y)


def internal_card(**kwargs) -> None:
    shape = [(kwargs['x0'] - X_MIN, kwargs['y0'] - Y_MIN),
             (kwargs['x1'] + X_MAX, kwargs['y0'] - Y_MIN),
             (kwargs['x1'] + X_MIN, kwargs['y1'] + Y_MIN),
             (kwargs['x0'] - X_MAX, kwargs['y1'] + Y_MIN)]
    card(shape=shape, date_function=_draw_internal_date, **kwargs)


def external_card(**kwargs):
    card_horizontal_middle = (kwargs['y0'] + kwargs['y1']) / 2

    shape = [(kwargs['x0'] - X_MAX, card_horizontal_middle),
             (kwargs['x0'] - X_MIN, kwargs['y0'] - Y_MIN),
             (kwargs['x1'] + X_MIN, kwargs['y0'] - Y_MIN),
             (kwargs['x1'] + X_MAX, card_horizontal_middle),
             (kwargs['x1'] + X_MIN, kwargs['y1'] + Y_MIN),
             (kwargs['x0'] - X_MIN, kwargs['y1'] + Y_MIN)]
    card(shape=shape, date_function=_draw_external_date, **kwargs)
