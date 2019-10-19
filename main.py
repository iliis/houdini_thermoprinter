#!/usr/bin/env python3

import sys
import time

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
    image_data = bytearray(0xFF & (0xFF ^ d) for d in i.tobytes())

    for chunk in chunker(image_data, 200*48):
        header(int(len(chunk)/48))
        printer.write(chunk)
        time.sleep(0.1)

if __name__ == "__main__":
    i = Image.new("1", (384, 300), 1)

    # Fass Gewichte: 8 und 8.5kg

    draw = ImageDraw.Draw(i)

    font_weight_big    = ImageFont.truetype('/home/samuel/.fonts/Blender/Blender-Heavy.otf', size=98) #118)
    font_weight_medium = ImageFont.truetype('/home/samuel/.fonts/Blender/Blender-Heavy.otf', size=50)
    font_text_normal   = ImageFont.truetype('/home/samuel/.fonts/Blender/Blender-Book.otf', size=36)

    weight = 8.4234232

    draw.text((-1,-25), f"{weight:07.4f}", font=font_weight_big, align="left")
    draw.text((332, 16), "KG", font=font_weight_medium)

    draw.text((0, 80), "19. Oktober 1970\n14:33.92", font=font_text_normal, align="left")
    draw.text((0, 170), "Gerät #43839\nWägung 394020", font=font_text_normal, align="left")

    i.save("test.png")

    sys.exit(0)

    #i = i.transpose(Image.ROTATE_270)

    with open("/dev/usb/lp0", "wb") as printer:
        print_image(printer, i)
        printer.write(bytearray([27, ord('d'), 7])) # feed N
