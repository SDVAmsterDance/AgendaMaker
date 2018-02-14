from typing import Union, Tuple

from PIL import ImageFont, ImageDraw

from agenda.utils import text
from agenda.utils.style import Style


class Shape:
    def __init__(self, x1=0, x0=0, y1=0, y0=0, style=Style()):
        self.x1 = x1
        self.x0 = x0
        self.y0 = y0
        self.y1 = y1

        self.style = style

        self.Y_MIN = style.scale * 10
        self.X_MAX = style.scale * 35
        self.X_MIN = style.scale * 20

        self.top_part = []
        self.right_part = []
        self.bottom_part = []
        self.left_part = []

    def get_shape(self):
        return self.top_part + self.right_part + self.bottom_part + self.left_part

    def set_cut(self, cut):
        card_horizontal_middle = (self.y0 + self.y1) / 2
        if 'l' in cut:
            self.left_part = [(self.x0 - self.X_MAX, self.y1 + self.Y_MIN),
                              (self.x0 - self.X_MAX, card_horizontal_middle + 10 * self.style.scale),
                              (self.x0 - self.X_MIN - 2 * self.style.scale,
                               card_horizontal_middle - 10 * self.style.scale),
                              (self.x0 - self.X_MIN - 2 * self.style.scale, self.y0 - self.Y_MIN)]
        if 'r' in cut:
            self.right_part = [(self.x1 + self.X_MAX, self.y0 - self.Y_MIN),
                               (self.x1 + self.X_MAX, card_horizontal_middle - 10 * self.style.scale),
                               (self.x1 + self.X_MIN - 2 * self.style.scale,
                                card_horizontal_middle + 10 * self.style.scale),
                               (self.x1 + self.X_MIN - 2 * self.style.scale, self.y1 + self.Y_MIN)]
        return self

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        pass


class Paralellogram(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.right_part = [(self.x1 + self.X_MAX, self.y0 - self.Y_MIN),
                           (self.x1 + self.X_MIN, self.y1 + self.Y_MIN)]
        self.left_part = [(self.x0 - self.X_MAX, self.y1 + self.Y_MIN),
                          (self.x0 - self.X_MIN, self.y0 - self.Y_MIN)]

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        """Draw the date on a specified position x on the event card."""
        card_height = (self.y1 + self.Y_MIN) - (self.y0 - self.Y_MIN)
        slope_width = self.X_MAX - self.X_MIN
        date_width = self.style.scale * 14
        draw.polygon([(self.x1 + self.X_MAX - date_width, self.y0 - self.Y_MIN),
                      (self.x1 + self.X_MAX, self.y0 - self.Y_MIN),
                      (self.x1 + self.X_MAX - date_width / (card_height / slope_width),
                       self.y0 - self.Y_MIN + date_width),
                      (self.x1 + self.X_MAX - date_width, self.y0 - self.Y_MIN + date_width)],
                     fill=background_color)

        text_x0 = text.vertical_center_text(date, font,
                                            x_min=self.x1 + self.X_MAX - date_width,
                                            x_max=self.x1 + self.X_MAX - (self.style.scale * 3))

        draw.text((text_x0, self.y0 - self.Y_MIN),
                  date,
                  font=font,
                  fill=text_color)


class Hexagon(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        card_horizontal_middle = (self.y0 + self.y1) / 2
        self.right_part = [(self.x1 + self.X_MIN, self.y0 - self.Y_MIN),
                           (self.x1 + self.X_MAX, card_horizontal_middle),
                           (self.x1 + self.X_MIN, self.y1 + self.Y_MIN)]
        self.left_part = [(self.x0 - self.X_MIN, self.y1 + self.Y_MIN),
                          (self.x0 - self.X_MAX, card_horizontal_middle),
                          (self.x0 - self.X_MIN, self.y0 - self.Y_MIN)]

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        """Draw the date on a specified position x on the event card."""
        card_horizontal_middle = (self.y1 + self.y0) / 2
        half_card_height = card_horizontal_middle - (self.y0 - self.Y_MIN)
        # red date
        slope_width = self.X_MAX - self.X_MIN
        half_date_height = font.getsize(date)[1] / 2
        intersect = (half_date_height / half_card_height) * slope_width
        draw.polygon([(self.x1 + self.X_MIN, card_horizontal_middle - half_date_height),
                      (self.x1 + self.X_MAX - intersect, card_horizontal_middle - half_date_height),
                      (self.x1 + self.X_MAX, card_horizontal_middle),
                      (self.x1 + self.X_MAX - intersect, card_horizontal_middle + half_date_height),
                      (self.x1 + self.X_MIN, card_horizontal_middle + half_date_height)],
                     fill=background_color)

        text_x0 = text.vertical_center_text(date, font,
                                            x_min=self.x1 + self.X_MIN,
                                            x_max=self.x1 + self.X_MAX - (self.style.scale * 3))

        draw.text((text_x0, card_horizontal_middle - half_date_height - (self.style.scale * 1)),
                  date,
                  font=font,
                  fill=text_color)
