from typing import Tuple, Union

from PIL import ImageDraw, ImageFont

from agenda.utils import style, text

import numpy as np

Y_MIN = style.scale * 10
X_MIN = style.scale * 20
X_MAX = style.scale * 35


def internal_card(draw: ImageDraw, x0: Union[int, float], x1: Union[int, float], y0: Union[int, float],
                  y1: Union[int, float], background_color: Tuple[int, int, int],
                  date_background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                  title_color: Tuple[int, int, int], date_text_color: Tuple[int, int, int],
                  title: str = "", date: tuple = (), details: str = "", start: Tuple[int, int] = None,
                  width: Union[int, float] = -1) -> None:

    # black card
    draw.polygon([(x0 - X_MIN, y0 - Y_MIN),
                  (x1 + X_MAX, y0 - Y_MIN),
                  (x1 + X_MIN, y1 + Y_MIN),
                  (x0 - X_MAX, y1 + Y_MIN)],
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
        draw_date(draw, date[0], x1, y0, y1, date_background_color, date_text_color, font)

        # Draw event details
        draw.multiline_text((x0 - X_MIN, y), details, font=font, fill=text_color, spacing=spacing)
    else:
        # Draw date boxes on every day of the event
        start_day = start[0]
        dates = [str(dat) for dat in np.arange(int(date[0]), int(date[1]) + 1, 1)]
        margin = style.scale * 40
        for i, date in enumerate(dates):
            x = ((start_day + 1 + i) * (width / 7)) - margin
            draw_date(draw, date, x, y0, y1, date_background_color, date_text_color, font)

        # Draw event details; display end time at the left side of the event box
        # Split string to display the start and end time at different positions
        location = ""
        start_time, end_time = details.split("-")
        start_time = "{}-...".format(start_time)
        try:
            end_time, price = end_time.split('\n')
        except:
            end_time, location, price = end_time.split('\n')
        end_time = "...-{}".format(end_time)

        # Draw the details in the event box
        draw.multiline_text((x0 - X_MIN, y), start_time, font=font, fill=text_color, spacing=spacing)
        draw.multiline_text((x1 - X_MIN, y), end_time, font=font, fill=text_color, spacing=spacing)
        if location:
            y += (style.scale * 10)
            draw.multiline_text((x0 - X_MIN, y), price, font=font, fill=text_color, spacing=spacing)
        y += (style.scale * 10)
        draw.multiline_text((x0 - X_MIN, y), price, font=font, fill=text_color, spacing=spacing)


def draw_date(draw: ImageDraw, date: str, x: Union[int, float], y0: Union[int, float],
              y1: Union[int, float], background_color: Tuple[int, int, int], text_color: Tuple[int, int, int], font: ImageFont):
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


def external_card(draw: ImageDraw, x0: Union[int, float], x1: Union[int, float], y0: Union[int, float],
                  y1: Union[int, float], background_color: Tuple[int, int, int],
                  date_background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                  title_color: Tuple[int, int, int], date_text_color: Tuple[int, int, int],
                  title: str = "", date: str = "", details: str = ""):

    card_horizontal_middle = (y1 + y0) / 2
    half_card_height = card_horizontal_middle - (y0 - Y_MIN)

    # hexagon
    draw.polygon([(x0 - X_MAX, card_horizontal_middle),
                  (x0 - X_MIN, y0 - Y_MIN),
                  (x1 + X_MIN, y0 - Y_MIN),
                  (x1 + X_MAX, card_horizontal_middle),
                  (x1 + X_MIN, y1 + Y_MIN),
                  (x0 - X_MIN, y1 + Y_MIN)],
                 fill=background_color)

    font = style.font(size=style.scale * 16)
    spacing = style.scale * -2
    y = y0 - Y_MIN
    title = text.wrap(string=title, font=font, width=(x1 + X_MIN) - (x0 - X_MIN))

    draw.multiline_text((x0 - X_MIN, y), title, font=font, fill=title_color, spacing=spacing)
    y += 2 * (style.scale * 14)  # 14 because that seems to be the line height
    font = style.font(size=style.scale * 13)
    details = text.wrap(string=details, font=font, width=(x1 + X_MIN) - (x0 - X_MIN))
    draw.multiline_text((x0 - X_MIN, y), details, font=font, fill=text_color, spacing=spacing)

    # red date
    slope_width = X_MAX - X_MIN
    half_date_height = font.getsize(date)[1] / 2
    intersect = (half_date_height / half_card_height) * slope_width
    draw.polygon([(x1 + X_MIN, card_horizontal_middle - half_date_height),
                  (x1 + X_MAX - intersect, card_horizontal_middle - half_date_height),
                  (x1 + X_MAX, card_horizontal_middle),
                  (x1 + X_MAX - intersect, card_horizontal_middle + half_date_height),
                  (x1 + X_MIN, card_horizontal_middle + half_date_height)],
                 fill=date_background_color)

    text_x0 = text.vertical_center_text(date, font,
                                        x_min=x1 + X_MIN, x_max=x1 + X_MAX - (style.scale * 3))

    draw.text((text_x0, card_horizontal_middle - half_date_height - (style.scale * 1)),
              date,
              font=font,
              fill=date_text_color)
