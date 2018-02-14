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

    def font(self, size=40):
        font = ImageFont.truetype('../resources/majalla.ttf', size * self.scale)
        return font


class AgendaStyle(Style):
    style_type = "agenda"
    scale = 2


class FlyerStyle(Style):
    style_type = "flyer"
