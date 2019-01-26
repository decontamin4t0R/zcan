#!/usr/bin/env python3

from mem_top import mem_top

import mapping2 as mapping
import asyncio
import websockets
import socket
import struct
import logging
import logging.handlers
import json
import requests
import datetime
import pytz
from tzlocal import get_localzone
from dateutil import parser
import math
import time

humidities={}
lastupdated={}
temperatures={}
names={}

@asyncio.coroutine 
def hello(uri):
    websocket = yield from websockets.connect(uri)
    while True:
        msg = yield from websocket.recv()
        info = json.loads(msg)
        #print(info)
        if 'state' in info and 'id' in info and info['id'] in names:
            name = names[info['id']]
            if 'temperature' in info['state']:
                temperatures[name] = info['state']['temperature']/100
                if data[key]['state']['lastupdated'] != "none":
                    lastupdated[name] = parser.parse(info['state']['lastupdated']+" UTC").astimezone(get_localzone())
                else:
                    lastupdated[name] = "none"
            if 'humidity' in info['state']:
                humidities[name] = info['state']['humidity']/100

can_frame_fmt = "=IB3x8s"

def dissect_can_frame(frame):
    can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
    if can_id & socket.CAN_RTR_FLAG != 0:
        print("RTR received from %08X"%(can_id&socket.CAN_EFF_MASK))
        return(0,0,[])
    can_id &= socket.CAN_EFF_MASK
    
    return (can_id, can_dlc, data[:can_dlc])

sensormap = {
        "temperature_inlet_before_recuperator": {"sensor":52,"type":"temperature"},
        "air_humidity_inlet_before_recuperator":{"sensor":53,"type":"humidity"},
        "temperature_inlet_after_recuperator": {"sensor":55,"type":"temperature"},
        "air_humidity_inlet_after_recuperator":{"sensor":54,"type":"humidity"},
        "temperature_outlet_before_recuperator": {"sensor":56,"type":"temperature"},
        "air_humidity_outlet_before_recuperator":{"sensor":58,"type":"humidity"},
        "temperature_outlet_after_recuperator": {"sensor":57,"type":"temperature"},
        "air_humidity_outlet_after_recuperator":{"sensor":59,"type":"humidity"},
    }

async def handle_client(cansocket):
    request = None
    while True:
        msg = await loop.sock_recv(cansocket, 16)
        can_id, can_dlc, data = dissect_can_frame(msg)
        if can_id & 0xFF800000 == 0:
            pdid = (can_id>>14)&0x7ff
            if pdid in mapping.mapping:
                stuff = mapping.mapping[pdid]
                if stuff["name"] in sensormap:
                    sensor = sensormap[stuff["name"]]
                    future1 = loop.run_in_executor(None, requests.put, f'{url}/{sensor["sensor"]}/state', json.dumps({f'{sensor["type"]}':stuff["transformation"](data)*100}))
                    loop.call_soon(future1)
                    #print(mem_top())


url = 'http://192.168.2.5/api/9E82617AE7/sensors'
response = requests.get(url)
#print(response.content.decode("utf-8") )

data = {}#json.loads(response.content.decode("utf-8") )
for key in data:
    if 'state' in data[key]:
        if 'temperature' in data[key]['state']:
            if "plug" in data[key]['modelid']:
                continue
            names[key] = data[key]['name']
            temperatures[names[key]] = data[key]['state']['temperature']/100
            if data[key]['state']['lastupdated'] != "none":
                lastupdated[names[key]] = parser.parse(data[key]['state']['lastupdated']+" UTC").astimezone(get_localzone())
            else:
                lastupdated[names[key]] = "none"
        elif 'humidity' in data[key]['state']:
            names[key] = data[key]['name']
            humidities[names[key]] = data[key]['state']['humidity']/100


# create a raw socket and bind it to the given CAN interface
loop = asyncio.get_event_loop()
while True:
    try: 
        s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind(("slcan0",))
        loop.run_until_complete(
                handle_client(s))
        
#            hello('ws://192.168.2.5:8088'))
    except:
        time.sleep(1)
        pass

# vim: et:sw=4:ts=4:smarttab:foldmethod=indent:si

