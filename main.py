#!/usr/bin/env python3

from houdinilib.app import Application

from printing import print_weight

class ScalePrintingApp(Application):
    def __init__(self):
        super(ScalePrintingApp, self).__init__()

        self.mi.register_handler("print_weight", self.on_print_weight)


    def on_print_weight(self, packet):
        print("got a packet!")
        print("weight:", packet['weight'])

        if not 'show_only' in packet:
            packet['show_only'] = False

        if not 'save_as_image' in packet:
            packet['save_as_image'] = False

        print_weight(float(packet['weight']), bool(packet['show_only']), bool(packet['save_as_image']))

if __name__ == "__main__":
    ScalePrintingApp().run()
