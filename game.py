import io
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

"""
# 縦方向・横方向リストについて

横方向リストである場合、リストがそのまま反映されます。
リストの先の要素の方が上です。

縦方向リストである場合、
リストの先の要素が一番左の列になります。

リストは縦横同じ長さです。
"""
default_mass = [
    [1, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0],
    [1, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 1],
]
wall = Image.open('images/wall.png')
none = Image.open('images/background.png')
panels = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]


def to_bytes(image):
    output_buffer = io.BytesIO()
    image.save(output_buffer, "png")
    output_buffer.seek(0)
    return output_buffer


def swap(line):
    """左によせる"""
    new = []
    fold = []
    while line:
        next_mass = line.pop(0)
        if next_mass == 1:
            if fold:
                new += fold
                fold = []
            new.append(next_mass)
            continue
        if next_mass == 0:
            fold.append(next_mass)
            continue
        new.append(next_mass)
    new += fold
    return new


def swap_right(line):
    line.reverse()
    new = swap(line)
    new.reverse()
    return new


def marge(line):
    """横のつながりをまーじする。右側にあるやつは0になる。
    * margeしたらswapする必要あり"""
    new = []
    while line:
        next_mass = line.pop(0)
        if not line:
            new.append(next_mass)
            continue

        next_next_mass = line[0]
        if next_mass == 1 or next_mass == 0:
            new.append(next_mass)
            continue
        if next_mass == next_next_mass:
            new.append(next_mass * 2)
            line.pop(0)
            new.append(0)
            continue
        new.append(next_mass)
    return new


def marge_right(line: list):
    new = marge(list(reversed(line)))
    new.reverse()
    return new


def transform_lengthwise_crosswise(mass):
    """縦方向リストから横方向リスト、またはその逆にする"""
    new = [[] for i in range(len(mass))]
    for x in range(len(mass)):
        for line in mass:
            new[x].append(line[x])
    return new


def move_right(mass):
    """
    右にずらす。横方向リストであれば右に、縦方向リストであれば下にずらす。
    :param mass: 盤面
    :return: list
    """
    new_mass = []
    for line in mass:
        new_mass.append(swap_right(marge_right(swap_right(line))))
    return new_mass


def move_left(mass):
    """
    左にずらす。横方向リストであれば左に、縦方向リストであれば上にずらす。
    :param mass:
    :return:
    """
    new_mass = []
    for line in mass:
        new_mass.append(
            swap(
                marge(
                    swap(
                        line
                    )
                )
            )
        )
    return new_mass


def generate_line(line):
    line_length = len(line)
    base_image = Image.new('RGBA', (line_length * 100, 100), (0, 0, 0, 0))
    i = 0
    for mass in line:
        if mass == 0:
            base_image.paste(none, (i, 0))
            i += 100
            continue
        if mass == 1:
            base_image.paste(wall, (i, 0))
            i += 100
            continue
        if mass in panels:
            base_image.paste(Image.open(f'images/{mass}.png'), (i, 0))
            i += 100
            continue
        image = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.font = ImageFont.truetype('CP Font.otf', 50)
        pos = (np.array(image.size) - np.array(draw.font.getsize(str(mass)))) / 2.
        draw.text(pos, str(mass), fill='#00bfff')
        base_image.paste(image, (i, 0))
        i += 100
    return base_image


def generate_mass(mass):
    line_count = len(mass)
    line_length = len(mass[0])
    base_image = Image.new('RGBA', (line_length * 100, line_count * 100), (0, 0, 0, 0))
    i = 0
    for line in mass:
        image = generate_line(line)
        base_image.paste(image, (0, i))
        i += 100

    return base_image


class Game2048:
    def __init__(self, bot, ctx, mass):
        self.bot = bot
        self.ctx = ctx
        self.mass = mass or default_mass

    def up(self):
        mass = transform_lengthwise_crosswise(self.mass)
        new_mass = move_left(mass)
        self.mass = transform_lengthwise_crosswise(new_mass)

    def down(self):
        mass = transform_lengthwise_crosswise(self.mass)
        new_mass = move_right(mass)
        self.mass = transform_lengthwise_crosswise(new_mass)

    def left(self):
        self.mass = move_left(self.mass)

    def right(self):
        self.mass = move_right(self.mass)

    def set_2(self):
        p = self.get_random_0()
        self.mass[p[0]][p[1]] = 2

    def get_random_0(self):
        positions = []
        for i, line in enumerate(self.mass):
            for i2, mass in enumerate(line):
                if mass == 0:
                    positions.append((i, i2))
        return random.choice(positions)

    def generate_mass_bytes(self):
        image = generate_mass(self.mass)
        return to_bytes(image)

    def has_0(self):
        for i, line in enumerate(self.mass):
            for i2, mass in enumerate(line):
                if mass == 0:
                    return True
        return False
