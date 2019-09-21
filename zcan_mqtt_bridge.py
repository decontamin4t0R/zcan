#!/usr/bin/env python3

from paho.mqtt import client as mqtt

import mapping2 as mapping
import asyncio
import socket
import struct
import time
import sys
from config import config

can_frame_fmt = "=IB3x8s"
mqtt_client = mqtt.Client()
mqtt_client.connect(config['mqtt_host'], config['mqtt_port'], 60)
mqtt_client.loop_start()

def dissect_can_frame(frame):
    can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
    if can_id & socket.CAN_RTR_FLAG != 0:
        print("RTR received from %08X"%(can_id&socket.CAN_EFF_MASK))
        return(0,0,[])
    can_id &= socket.CAN_EFF_MASK
    
    return (can_id, can_dlc, data[:can_dlc])

@asyncio.coroutine
def handle_client(cansocket):
    request = None
    while True:
        msg = yield from loop.sock_recv(cansocket, 16)
        can_id, can_dlc, data = dissect_can_frame(msg)
        if can_id & 0xFF800000 == 0:
            pdid = (can_id>>14)&0x7ff
            if pdid in mapping.mapping:
                stuff = mapping.mapping[pdid]
                topic = "lueftung/zehnder/state/%s" % stuff["name"]
                info = stuff["transformation"](data)
                mqtt_client.publish(topic, info, retain=True)
                print("Pushing to %i %s %s" % (pdid, topic, str(info)))
            else:
                print("Unknown message %i %s" % (pdid, repr(data)), file=sys.stderr)

# create a raw socket and bind it to the given CAN interface
loop = asyncio.get_event_loop()
s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((config['can_if'],))
loop.run_until_complete(
        handle_client(s))

# vim: et:sw=4:ts=4:smarttab:foldmethod=indent:si


