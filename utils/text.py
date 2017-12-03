from typing import Union

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont


def small_caps(draw, coords, string, font, fill):
    [x, y] = coords
    _, h = font.getsize(string)
    small_font = ImageFont.truetype(font.path, int(font.size * 0.68))
    print(small_font.size)
    for c in string:
        if c.islower():
            w, h2 = draw.textsize(c.upper(), small_font)
            draw.text([x, y + h - h2], c.upper(), font=small_font, fill=fill)
        else:
            w, _ = draw.textsize(c, font)
            draw.text([x, y], c, font=font, fill=fill)
        x += w


def vertical_center_text(string: str, font: FreeTypeFont, x_min, x_max):
    text_w, _ = font.getsize(string)
    text_x0 = ((x_min + x_max) / 2) - (text_w / 2)
    return text_x0


def wrap(string: str, font: FreeTypeFont, width: Union[int, float]):
    wrapped_list = []
    wrapped = ""
    length = 0
    for word in string.split(" "):
        word_lenght = font.getsize(word)[0]
        if length + word_lenght < width:
            wrapped_list.append(word)
            length += word_lenght
        else:
            wrapped += "\n" + " ".join(wrapped_list)
            wrapped_list = [word]
            length = word_lenght
    wrapped += "\n" + " ".join(wrapped_list)
    return wrapped.strip()
