from __future__ import annotations
from PIL import Image
from typing import Union
from type_hints import RGB
from type_hints import RGBA
from type_hints import ScreenBox


def adjust_color(color: Union[RGBA, RGB], fuzziness: int = 5) -> Union[RGBA, RGB]:
    '''
    Adjusts the color of a pixel.
    '''
    assert fuzziness > 1
    detail = 1 << (fuzziness - 1)
    try:
        r, g, b, a = color
        r = (r + detail // 2) // detail * detail
        g = (g + detail // 2) // detail * detail
        b = (b + detail // 2) // detail * detail
        return r, g, b, a
    except ValueError:
        r, g, b = color
        r = (r + detail // 2) // detail * detail
        g = (g + detail // 2) // detail * detail
        b = (b + detail // 2) // detail * detail
        return r, g, b


class Img:
    def __init__(self, image_file: str):
        self.image_file = image_file
        self.image = Image.open(image_file)
        self.colors = None

    def fuzzify(self, fuzziness: int = 5) -> Img:
        pixels = self.image.load()
        width, height = self.image.size
        for x in range(width):
            for y in range(height):
                pixels[x, y] = adjust_color(pixels[x, y], fuzziness)
        return self

    def save_as(self, output_file: str) -> Img:
        self.image.save(output_file)
        return self

    def crop(self, box: ScreenBox) -> Img:
        self.image = self.image.crop(box)
        return self

    def extract(self, output_file: str, box: ScreenBox) -> Img:
        self.image.crop(box).save(output_file)
        return self

    def get_colors(self) -> dict[RGB, int]:
        if self.colors is not None:
            return self.colors
        self.colors = dict()
        pixels = self.image.load()
        width, height = self.image.size
        for x in range(width):
            for y in range(height):
                color = pixels[x, y][:3]
                self.colors[color] = self.colors.get(color, 0) + 1
        return self.colors
