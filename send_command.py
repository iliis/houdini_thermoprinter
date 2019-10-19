#!/usr/bin/env python3
import json
import socket
import sys
import argparse

from houdinilib.management_interface import PacketParser

parser = argparse.ArgumentParser(description='Send a generic command to the crossword server app')

parser.add_argument('-p', '--port', type=int, default=1234, help='Destination port')
parser.add_argument('-a', '--address', default='localhost', help='Destination address')
parser.add_argument('-l', '--listen', action="store_true", default=False, help="Listen for an answer after sending command.")
parser.add_argument('command', help="the command to send")
parser.add_argument('parameters', nargs='*', help="arbitrary parameters to send in the format key=value")

args = parser.parse_args()




# set up connection
con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
con.connect( (args.address, args.port) )

print("connected to", con.getpeername())

parser = PacketParser()


def send(pkt):
    data = json.dumps(pkt)
    pkt = "{}\n{}\n".format(len(data), data).encode('ascii')
    print("sending raw command: '{}'".format(pkt))
    con.sendall(pkt)

    print("sent command")


def receive():
    data = con.recv(4096)
    for packet in parser.receive(data):
        print("got reply:")
        print(json.loads(packet))

if args.command == "just_listen":
    while True:
        listen()

# parse additional parameters
cmd = {'command': args.command}

for param in args.parameters:
    key, value = param.split('=')
    if key in cmd:
        print(f"Warning: Overwriting existing parameter {key} = '{cmd[key]}' with 'value'")
    cmd[key] = value

send(cmd)

if args.listen:
    receive()
