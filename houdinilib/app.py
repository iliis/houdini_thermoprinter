import datetime
import curses
import json
import logging
import os
import selectors
import subprocess
import sys
import time
import traceback
import signal

#from helpers import *
from houdinilib.management_interface import ManagementInterface

# make sure logfile doesn't grow unboundedly
if os.path.exists("application.log") and os.path.getsize("application.log") > 1024*1024*10: # limit: 10MB
    print("[{}] deleting huge logfile".format(datetime.datetime.now()))
    os.remove("application.log")


log = logging.getLogger('application')
hdlr = logging.FileHandler('application.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)



def git_cmd(params):
    log.debug("Executing git command: {}".format(params))
    try:
        label = subprocess.check_output(
                    params,
                    cwd=os.path.dirname(os.path.realpath(__file__))).decode('utf8').strip()

        if len(label) == 0:
            return "UNKNOWN"
        else:
            return label
    except Exception as e:
        log.error("Unhandled Exception: {}".format(e))
        log.debug(traceback.format_exc())
        return "UNKNOWN (err)"

def get_version():
    return git_cmd(["git", "describe", "--always", "--tags"])

def get_version_date():
    return git_cmd(["git", "log", "-1", "--format=%cd"])




class Application:
    def __init__(self):
        self.sel = selectors.DefaultSelector()

        self.is_running = False
        # create server for remote control
        self.mi = ManagementInterface(1234, self.sel)
        log.info("local address: {}".format(self.mi.get_local_addresses()))

        self.mi.register_handler('quit', self.exit_app_by_packet)
        self.mi.register_handler('shutdown', self.shutdown)

    def __del__(self):
        self.exit()


    def exit_app_by_packet(self, packet):
        log.info("Exiting application trough remote command.")
        self.exit()

    def exit(self):
        self.is_running = False

    def shutdown(self, packet):
        log.info("Shutting down PC!!")
        subprocess.call(["sudo", "halt"])

    def run(self):
        self.is_running = True

        while self.is_running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

