#!/usr/bin/env python3

import math
import sys
import time
from datetime import datetime
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from PIL import Image, ImageDraw, ImageFont

from houdinilib.helpers import layout_text

log = logging.getLogger('root')

# based on https://stackoverflow.com/a/434328
def chunker(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]

def print_image(printer, image):
    def header(h):
        w = 48 # 48 bytes per line = 384 pixels
        printer.write(bytearray([
            29, 0x76, 0x30,
                0, # no scaling
                w, 0, h, 0
            ]))

    # invert data: 0 = black in image -> must be 1 to print "ink"
    image_data = bytearray(0xFF & (0xFF ^ d) for d in image.tobytes())

    for chunk in chunker(image_data, 20*48):
        header(int(len(chunk)/48))
        printer.write(chunk)
        #time.sleep(0.1)


def get_and_increment_counter():

    try:
        with open('counter.txt', 'r') as f:
            counter = int(f.readline())
            log.info(f"got counter from file: {counter}")
    except FileNotFoundError:
        counter = 0
        log.warning("no counter value file found, resetting to 0")
    except Exception as e:
        counter = 0
        log.error("Something went wrong when reading the counter file: {}".format(e))

    counter += 1

    with open('counter.txt', 'w') as f:
        f.write(str(counter))

    return counter

def draw_text_rightaligned(draw, xy, text, font):
    width, height = draw.textsize(text, font)
    draw.text((xy[0]-width, xy[1]), text, font=font)

def get_logo():
    logo = Image.open("logo.png")
    buf = Image.new("1", (384, logo.size[1]), 1)
    draw = ImageDraw.Draw(buf)
    draw.bitmap((0,0), logo)
    return buf



def print_weight(weight, show_only=False, save_as_image=True):

    img = Image.new("1", (384, 330), 1)

    # Fass Gewichte: 8 und 8.5kg

    draw = ImageDraw.Draw(img)

    font1  = 'fonts/TungstenNarrow-Light.otf'
    font2 = 'fonts/Blender-Book.otf'

    font_weight_big    = ImageFont.truetype(font1, size=200)
    font_weight_medium = ImageFont.truetype(font1, size=110)
    font_text_normal   = ImageFont.truetype(font2, size=33)

    y = 0

    #draw.text((0,y), "Trudi's Allerlei", font=font_text_normal, align="left")
    #y += 40

    # we want 5 digits in total
    # we also want at least one digit before the decimal point
    # and we always want all the digits after the decimal points even if they are zero

    if weight < 0:
        log.warning("Not printing negative weight: {weight}")
        weight = 0

    # number of digits left of the decimal point
    num_digits = max(0, int(math.log10(weight))) + 1

    if num_digits > 4:
        weight_str = f"9999"
        fmt = 0
    elif num_digits == 0:
        weight_str = f"{weight:.3f}"
    else:
        weight_str = f"{weight:.{4-num_digits}f}"

    log.info("Printing weight {} as string: '{}' (num_digits: {})".format(weight, weight_str, num_digits))

    draw_text_rightaligned(draw, (310, y), weight_str, font_weight_big)

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
        print_image(printer, get_logo())
        print_image(printer, img)
        printer.write(b"\n\n")
        #printer.write(bytearray([27, ord('d'), 50])) # feed N

def print_text_raw(text):
    with open("/dev/usb/lp0", "wb") as printer:
        log.debug(f"raw text: '{text}'")

        print_image(printer, get_logo())
        printer.write(b"\n\n")
        #printer.write(bytearray([0x18, 0x74, 115]))
        printer.write(bytearray([0x1B, 0x74, 3]))
        #printer.write( ("\n".join(layout_text(text, 32))).encode('utf8') )
        printer.write(bytearray([i for i in range(50, 256)]))
        printer.write(b" \n \n \n \n \n")

def print_text(text):
    with open("/dev/usb/lp0", "wb") as printer:
        padding_top = 20

        print_image(printer, get_logo())

        font = ImageFont.truetype('fonts/Blender-Book.otf', size=37)


        # measure how long our text will be in pixels
        img = Image.new("1", (384, 100), 1)
        draw = ImageDraw.Draw(img)

        max_length = 50
        tw = 10000

        log.debug(f"layouting text with {len(text)} chars")

        while tw > img.size[0] and max_length > 10:

            # keep line length in check (this assumes a monospaced font, which we don't have!0
            log.debug(f"testing layouting text with {len(text)} chars {max_length}")
            layouted_text = "\n".join(layout_text(text, max_length))

            # why can't I call this without having a picture first??
            tw, th = draw.textsize(layouted_text, font=font)

            max_length -= 1

        text = layouted_text
        log.debug(f"wrapped text with max_length = {max_length+1} chars = {tw} px -> {th} high")

        # create image with the correct size
        img = Image.new("1", (384, th+padding_top), 1)
        draw = ImageDraw.Draw(img)

        draw.multiline_text((0,padding_top), text, font=font)

        img.save("test.png")

        print_image(printer, img)
        printer.write(b" \n\n\n\n")


if __name__ == "__main__":
    #print_weight(0.01, show_only=False, save_as_image=True)

    print_text("hallo welt äöüÄÖÜ asdif sa ifdsahfiew hfawuf hasd hfsa yfhsa ygfsa yfgsa yfusayfeweureg iasdid j jdsksk dsal dsl dsl dl dl dl dl dl dl dl dl dl dldiei aijdsdsahu ehuahudshudsu da dshu dsh dhu duh")
