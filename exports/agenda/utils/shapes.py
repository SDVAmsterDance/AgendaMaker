from typing import Tuple

from PIL import ImageFont, ImageDraw
from exports.agenda.utils.style import Style

from exports.agenda.utils import text


class Shape:
    def __init__(self, x1=0, x0=0, y1=0, y0=0, style=Style()):
        self.x1 = x1
        self.x0 = x0
        self.y0 = y0
        self.y1 = y1

        self.style = style

        self.top_part = []
        self.right_part = []
        self.bottom_part = []
        self.left_part = []

    def get_shape(self):
        return self.top_part + self.right_part + self.bottom_part + self.left_part

    def set_cut(self, cut):
        card_horizontal_middle = (self.y0 + self.y1) / 2
        if 'l' in cut:
            self.left_part = [(self.x0 - self.x_max(), self.y1 + self.y_min()),
                              (self.x0 - self.x_max(), card_horizontal_middle + 10 * self.style.scale),
                              (self.x0 - self.x_min() - 2 * self.style.scale,
                               card_horizontal_middle - 10 * self.style.scale),
                              (self.x0 - self.x_min() - 2 * self.style.scale, self.y0 - self.y_min())]
        if 'r' in cut:
            self.right_part = [(self.x1 + self.x_max(), self.y0 - self.y_min()),
                               (self.x1 + self.x_max(), card_horizontal_middle - 10 * self.style.scale),
                               (self.x1 + self.x_min() - 2 * self.style.scale,
                                card_horizontal_middle + 10 * self.style.scale),
                               (self.x1 + self.x_min() - 2 * self.style.scale, self.y1 + self.y_min())]
        return self

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        pass

    def get_height(self):
        return self.y1 - self.y0

    def get_scaled_height(self):
        return self.get_height() / self.style.scale

    def get_width(self):
        return self.x1 - self.x0

    def get_scaled_width(self):
        return self.get_width() / self.style.scale

    def x_min(self):
        return int(self.get_scaled_height() * self.style.x_min)

    def x_max(self):
        return int(self.get_scaled_height() * self.style.x_max)

    def y_min(self):
        return int(self.get_scaled_height() * self.style.y_min)


class Paralellogram(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.right_part = [(self.x1 + self.x_max(), self.y0 - self.y_min()),
                           (self.x1 + self.x_min(), self.y1 + self.y_min())]
        self.left_part = [(self.x0 - self.x_max(), self.y1 + self.y_min()),
                          (self.x0 - self.x_min(), self.y0 - self.y_min())]

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        """Draw the date on a specified position x on the event card."""
        card_height = (self.y1 + self.y_min()) - (self.y0 - self.y_min())
        slope_width = self.x_max() - self.x_min()
        date_width = font.size
        draw.polygon([(self.x1 + self.x_max() - date_width, self.y0 - self.y_min()),
                      (self.x1 + self.x_max(), self.y0 - self.y_min()),
                      (self.x1 + self.x_max() - date_width / (card_height / slope_width),
                       self.y0 - self.y_min() + date_width),
                      (self.x1 + self.x_max() - date_width, self.y0 - self.y_min() + date_width)],
                     fill=background_color)

        text_x0 = text.vertical_center_text(date, font,
                                            x_min=self.x1 + self.x_max() - date_width,
                                            x_max=self.x1 + self.x_max() - (self.style.scale * 3))

        draw.text((text_x0, self.y0 - self.y_min()),
                  date,
                  font=font,
                  fill=text_color)


class Hexagon(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        card_horizontal_middle = (self.y0 + self.y1) / 2
        self.right_part = [(self.x1 + self.x_min(), self.y0 - self.y_min()),
                           (self.x1 + self.x_max(), card_horizontal_middle),
                           (self.x1 + self.x_min(), self.y1 + self.y_min())]
        self.left_part = [(self.x0 - self.x_min(), self.y1 + self.y_min()),
                          (self.x0 - self.x_max(), card_horizontal_middle),
                          (self.x0 - self.x_min(), self.y0 - self.y_min())]

    def draw_date(self, draw: ImageDraw, date: str, background_color: Tuple[int, int, int],
                  text_color: Tuple[int, int, int], font: ImageFont):
        """Draw the date on a specified position x on the event card."""
        card_horizontal_middle = (self.y1 + self.y0) / 2
        half_card_height = card_horizontal_middle - (self.y0 - self.y_min())
        # red date
        slope_width = self.x_max() - self.x_min()
        half_date_height = font.getsize(date)[1] / 2
        intersect = (half_date_height / half_card_height) * slope_width
        draw.polygon([(self.x1 + self.x_min(), card_horizontal_middle - half_date_height),
                      (self.x1 + self.x_max() - intersect, card_horizontal_middle - half_date_height),
                      (self.x1 + self.x_max(), card_horizontal_middle),
                      (self.x1 + self.x_max() - intersect, card_horizontal_middle + half_date_height),
                      (self.x1 + self.x_min(), card_horizontal_middle + half_date_height)],
                     fill=background_color)

        text_x0 = text.vertical_center_text(date, font,
                                            x_min=self.x1 + self.x_min(),
                                            x_max=self.x1 + self.x_max() - (self.style.scale * 3))

        draw.text((text_x0, card_horizontal_middle - half_date_height - (self.style.scale * 1)),
                  date,
                  font=font,
                  fill=text_color)
