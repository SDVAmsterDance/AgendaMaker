from PIL import ImageFont


class Style:
    color = dict(red=(237, 31, 36),
                 black=(0, 0, 0),
                 lblack=(136, 136, 136),
                 white=(255, 255, 255),
                 lwhite=(238, 238, 238),
                 dred=(171, 37, 37),
                 ldred=(171, 117, 117),
                 lred=(247, 128, 128)
                 )
    style_type = ""
    scale = 1

    x_min = 1.1
    x_max = 2
    y_min = 0.45


    def font(self, size=40):
        font = ImageFont.truetype('../resources/majalla.ttf', size * self.scale)
        return font


class AgendaStyle(Style):
    style_type = "agenda"
    scale = 2
    margin = 42
    Y_MIN = scale * 10
    X_MAX = scale * 45
    X_MIN = scale * 25


class FlyerStyle(Style):
    style_type = "flyer"
    x_min = .5
    x_max = .8
    y_min = 0

    margin = (90, 20)
    Y_MIN = X_MIN = X_MAX = 0

    def __init__(self):
        self.Y_MIN = self.scale * 10
        self.X_MIN = self.scale * 20
        self.X_MAX = self.scale * 35
