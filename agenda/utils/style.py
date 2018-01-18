from PIL import ImageFont

color = dict(red=(237, 31, 36),
             black=(0, 0, 0),
             lblack=(136, 136, 136),
             white=(255, 255, 255),
             lwhite=(238, 238, 238),
             dred=(171, 37, 37),
             ldred=(171, 117, 117),
             lred=(247, 128, 128)
             )


def font(size=40, style=None):
    font = ImageFont.truetype('resources/majalla.ttf', size)
    return font





