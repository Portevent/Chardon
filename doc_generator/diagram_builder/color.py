import logging


class Color:

    def __init__(self, int_value=None, rgb=None, hsv=None):
        self.r = 255
        self.g = 255
        self.b = 255

        if int_value is not None:
            self.r, self.g, self.b = self.INT2RGB(int_value)

        if rgb is not None:
            if len(rgb) != 3:
                raise ValueError(f'RGB given is not a list of 3 integer : {rgb=}')

            self.r, self.g, self.b = rgb

        if hsv is not None:
            if len(rgb) != 3:
                raise ValueError(f'HSV given is not a list of 3 integer : {rgb=}')

            self.r, self.g, self.b = self.HSV2RGB(*hsv)

    def addHSV(self, hue=0, saturation=0, value=0):
        # logging.debug(f'Adding {hue=} {saturation=} {value=}')
        # logging.debug(f'Old RGB {self.r} {self.g} {self.b}')
        h, s, v = self.RGB2HSV(self.r, self.g, self.b)
        # logging.debug(f'Old HSV {h=} {s=} {v=}')
        h += hue
        s += saturation
        v += value

        h = h % 360
        s = min(1, max(0, s))  # Clamp to [0, 1]
        v = min(1, max(0, v))  # Clamp to [0, 1]
        # logging.debug(f'New HSV {h=} {s=} {v=}')
        self.r, self.g, self.b = self.HSV2RGB(h, s, v)
        # logging.debug(f'New RGB {self.r} {self.g} {self.b}')

    def getInt(self):
        return self.RGB2INT(self.r, self.g, self.b)

    @staticmethod
    def INT2RGB(int_value):
        return ((int_value >> 16) & 255)/255, ((int_value >> 8) & 255)/255, (int_value & 255)/255

    @staticmethod
    def RGB2INT(r, g, b):
        return (int(r*255) << 16) + (int(g*255) << 8) + int(b*255)

    @staticmethod
    def RGB2HSV(r, g, b):
        values = {'r': r, 'b': b, 'g': g}
        if r >= g:
            if r >= b:
                maxColor = 'r'
                minColor = 'b' if b < g else 'g'
            else:
                maxColor = 'b'
                minColor = 'g'
        else:
            if r >= b:
                maxColor = 'g'
                minColor = 'b'
            else:
                minColor = 'r'
                maxColor = 'g' if g > b else 'b'

        v = values[maxColor]
        c = v - values[minColor]

        if c == 0:
            h = 0
        else:
            match maxColor:
                case 'r':
                    h = ((g - b) / c) % 6
                case 'g':
                    h = ((b - r) / c) + 2
                case 'b':
                    h = ((r - g) / c) + 4

            h *= 60

        if v == 0:
            s = 0
        else:
            s = c / v

        return h, s, v

    @staticmethod
    def HSV2RGB(h, s, v):
        if h < 0 or h > 360:
            raise ValueError(f'Couldn\'t convert {(h,s,v)=} to RGB ({h=} should be within [0,360[')

        c = v * s
        h_ = h / 60
        x = c * (1 - abs(h_ % 2 - 1))
        m = v - c / 1

        if h_ < 1:
            r, g, b = (c, x, 0)
        elif h_ < 2:
            r, g, b = (x, c, 0)
        elif h_ < 3:
            r, g, b = (0, c, x)
        elif h_ < 4:
            r, g, b = (0, x, c)
        elif h_ < 5:
            r, g, b = (x, 0, c)
        else:
            r, g, b = (c, 0, x)

        return r + m, g + m, b + m
