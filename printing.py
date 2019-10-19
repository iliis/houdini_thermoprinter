#!/usr/bin/env python3

import sys
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


# based on https://stackoverflow.com/a/434328
def chunker(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]

def print_image(printer, image):
    def header(h):
        #print(f"printing {h} lines")
        w = 48 # 48 bytes per line = 384 pixels
        printer.write(bytearray([
            29, 0x76, 0x30,
                0, # no scaling
                w, 0, h, 0
            ]))

    # invert data: 0 = black in image -> must be 1 to print "ink"
    image_data = bytearray(0xFF & (0xFF ^ d) for d in image.tobytes())

    for chunk in chunker(image_data, 200*48):
        header(int(len(chunk)/48))
        printer.write(chunk)
        time.sleep(0.1)


def get_and_increment_counter():

    try:
        with open('counter.txt', 'r') as f:
            counter = int(f.readline())
            print("got counter from file:", counter)
    except FileNotFoundError:
        counter = 0
        print("no counter value file found, resetting to 0")

    counter += 1

    with open('counter.txt', 'w') as f:
        f.write(str(counter))

    return counter

def draw_text_rightaligned(draw, xy, text, font):
    width, height = draw.textsize(text, font)
    draw.text((xy[0]-width, xy[1]), text, font=font)

def print_weight(weight, show_only=False, save_as_image=True):

    logo = Image.open("logo.png")

    img = Image.new("1", (384, 330), 1)

    # Fass Gewichte: 8 und 8.5kg

    draw = ImageDraw.Draw(img)

    font1  = 'fonts/TungstenNarrow-Light.otf'
    font2 = 'fonts/Blender-Book.otf'

    font_weight_big    = ImageFont.truetype(font1, size=200)
    font_weight_medium = ImageFont.truetype(font1, size=110)
    font_text_normal   = ImageFont.truetype(font2, size=33)

    y = 0

    draw.bitmap((0,y), logo)

    y += 50

    #draw.text((0,y), "Trudi's Allerlei", font=font_text_normal, align="left")
    #y += 40

    # we want 5 significant digits in total
    # but we also want at least one digit before the decimal point
    if weight >= 1:
        weight_str = f"{weight:.5g}"
    else:
        weight_str = f"{weight:.4f}"

    draw_text_rightaligned(draw, (315, y), weight_str, font_weight_big)

    draw.text((323, y+70), "KG", font=font_weight_medium)

    y += 190

    now = datetime.now()

    timestr = now.strftime("%d. %B 1985, %H:%M:%S")

    draw.text((0, y), timestr, font=font_text_normal, align="left")
    y += 40

    counter = get_and_increment_counter()

    draw.text((0, y), f"Gerät #438, Wägung #{counter}", font=font_text_normal, align="left")

    if save_as_image:
        img.save("test.png")

    if show_only:
        return

    with open("/dev/usb/lp0", "wb") as printer:
        print_image(printer, img)
        printer.write(bytearray([27, ord('d'), 5])) # feed N
