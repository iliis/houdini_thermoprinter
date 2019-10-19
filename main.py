#!/usr/bin/env python3

import os
import logging

from houdinilib.app import Application

from printing import print_weight

log = logging.getLogger('root')


class ScalePrintingApp(Application):
    def __init__(self):
        super(ScalePrintingApp, self).__init__()

        self.mi.register_handler("print_weight", self.on_print_weight)


    def on_print_weight(self, packet):
        log.info(f"got a command to print! weight: {packet['weight']}")

        if not 'show_only' in packet:
            packet['show_only'] = False

        if not 'save_as_image' in packet:
            packet['save_as_image'] = False

        print_weight(float(packet['weight']), bool(packet['show_only']), bool(packet['save_as_image']))

if __name__ == "__main__":
    # quick hack to access files using relative pathnames
    # I think the real proper way to do this would be to use
    # importlib.resources, but that seems unnecessarily complicated for our
    # case (we won't be deploying this application as a zipped egg file)
    os.chdir(os.path.dirname(__file__))

    ScalePrintingApp().run()
