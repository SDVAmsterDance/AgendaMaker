from typing import Tuple, Union

from PIL import ImageDraw

from agenda.utils import style, text


def internal_card(draw: ImageDraw, x0: Union[int, float], x1: Union[int, float], y0: Union[int, float],
                  y1: Union[int, float], background_color: Tuple[int, int, int],
                  date_background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                  title_color: Tuple[int, int, int], date_text_color: Tuple[int, int, int],
                  title: str = "", date: str = "", details: str = "") -> None:
    y_min = style.scale * 10
    x_min = style.scale * 20
    x_max = style.scale * 35

    # black card
    draw.polygon([(x0 - x_min, y0 - y_min),
                  (x1 + x_max, y0 - y_min),
                  (x1 + x_min, y1 + y_min),
                  (x0 - x_max, y1 + y_min)],
                 fill=background_color)

    font = style.font(size=style.scale * 16)
    spacing = style.scale * -2
    y = y0 - y_min
    title = text.wrap(string=title, font=font, width=(x1 + x_min) - (x0 - x_min))

    draw.multiline_text((x0 - x_min, y), title, font=font, fill=title_color, spacing=spacing)
    y += 2 * (style.scale * 14)  # 14 because that seems to be the line height
    font = style.font(size=style.scale * 13)
    details = text.wrap(string=details, font=font, width=(x1 + x_min) - (x0 - x_min))
    draw.multiline_text((x0 - x_min, y), details, font=font, fill=text_color, spacing=spacing)

    # red date
    if date:
        card_height = (y1 + y_min) - (y0 - y_min)
        slope_width = x_max - x_min
        date_width = style.scale * 14
        draw.polygon([(x1 + x_max - date_width, y0 - y_min),
                      (x1 + x_max, y0 - y_min),
                      (x1 + x_max - date_width / (card_height / slope_width), y0 - y_min + date_width),
                      (x1 + x_max - date_width, y0 - y_min + date_width)],
                     fill=date_background_color)

        text_x0 = text.vertical_center_text(date, font,
                                            x_min=x1 + x_max - date_width, x_max=x1 + x_max - (style.scale * 3))

        draw.text((text_x0, y0 - y_min),
                  date,
                  font=font,
                  fill=date_text_color)


def external_card(draw: ImageDraw, x0: Union[int, float], x1: Union[int, float], y0: Union[int, float],
                  y1: Union[int, float], background_color: Tuple[int, int, int],
                  date_background_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                  title_color: Tuple[int, int, int], date_text_color: Tuple[int, int, int],
                  title: str = "", date: str = "", details: str = ""):
    y_min = style.scale * 10
    x_min = style.scale * 20
    x_max = style.scale * 35
    card_horizontal_middle = (y1 + y0) / 2
    half_card_height = card_horizontal_middle - (y0 - y_min)

    # hexagon
    draw.polygon([(x0 - x_max, card_horizontal_middle),
                  (x0 - x_min, y0 - y_min),
                  (x1 + x_min, y0 - y_min),
                  (x1 + x_max, card_horizontal_middle),
                  (x1 + x_min, y1 + y_min),
                  (x0 - x_min, y1 + y_min)],
                 fill=background_color)

    font = style.font(size=style.scale * 16)
    spacing = style.scale * -2
    y = y0 - y_min
    title = text.wrap(string=title, font=font, width=(x1 + x_min) - (x0 - x_min))

    draw.multiline_text((x0 - x_min, y), title, font=font, fill=title_color, spacing=spacing)
    y += 2 * (style.scale * 14)  # 14 because that seems to be the line height
    font = style.font(size=style.scale * 13)
    details = text.wrap(string=details, font=font, width=(x1 + x_min) - (x0 - x_min))
    draw.multiline_text((x0 - x_min, y), details, font=font, fill=text_color, spacing=spacing)

    # red date
    slope_width = x_max - x_min
    half_date_height = font.getsize(date)[1] / 2
    intersect = (half_date_height / half_card_height) * slope_width
    draw.polygon([(x1 + x_min, card_horizontal_middle - half_date_height),
                  (x1 + x_max - intersect, card_horizontal_middle - half_date_height),
                  (x1 + x_max, card_horizontal_middle),
                  (x1 + x_max - intersect, card_horizontal_middle + half_date_height),
                  (x1 + x_min, card_horizontal_middle + half_date_height)],
                 fill=date_background_color)

    text_x0 = text.vertical_center_text(date, font,
                                        x_min=x1 + x_min, x_max=x1 + x_max - (style.scale * 3))

    draw.text((text_x0, card_horizontal_middle - half_date_height - (style.scale * 1)),
              date,
              font=font,
              fill=date_text_color)
