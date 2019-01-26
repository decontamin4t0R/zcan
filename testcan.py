#!/usr/bin/python3

import asynchat
import asyncore
import socket
import threading
import time
import optparse
import sys
from time import sleep
import struct
import re
import logging
import logging.handlers
import datetime
import os
import math
import mapping2 as mapping
import traceback
import json
import ComfoNetCan as CN

# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"

def dissect_can_frame(frame):
        can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
        if can_id & socket.CAN_RTR_FLAG != 0:
            print("RTR received from %08X"%(can_id&socket.CAN_EFF_MASK))
            return(0,0,[])
        can_id &= socket.CAN_EFF_MASK
        
        return (can_id, can_dlc, data[:can_dlc])

class sink():
    def __init__(self):
        pass
    
    def push(self, msg):
        pass
 
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
       self.logger = logger
       self.log_level = log_level
       self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

class Redirector:
    def __init__(self, socketCAN, client, spy=False):
        self.SCan = socketCAN
        self.connection = client
        self.spy = spy
        self._write_lock = threading.Lock()
        self.power = 0
        self.sendpoweron = 0
        self.sendpoweroff = 0
        self.tempspy = 0
        self.clickcount = 0
        self.clickflag = False 
        self.activated = True 
        self.activetime = 0 
        self.time = 0 
        self.last_steering_key = [0xC0,0x00]
        self.AI=-1
        self.lastpos = -1
        self.d1B8 = [0x0F,0xC0,0xF6,0xFF,0x60,0x21]
        self.aux = False
        self.torque = 0
        self.power = 0
        self.torquecnt = 0
        self.consumecnt = 0
        self.consumed = 0
        self.consumption = 0.0
        self.speed = 0
        self.status = {
            "Power":"Off",
            "Running":"Off",
            "Volts":" 0.00",
        }
        self.kwplist = []
        self.kwpdata = []
        self.kwpsource = -1
        self.kwpenable = True
        self.canlist={}
        for n in dir(self):
            if n[0:3] == 'can':
                func = getattr(self, n)
                if callable(func):
                    can_id = int(n[3:],16)
                    self.canlist[can_id]=func
        print(self.canlist)
        self.cnet = CN.ComfoNet(self.SCan)
        self.cnet.FindComfoAirQ()

    def shortcut(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial->socket')
        self.thread_read.start()
        self.writer()

    def _readline(self):
        eol = b'\r'
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self.serial.read(1)
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        return bytes(line)

    def _sendkey(self, key):
        if self.connection is not None:
        #try:
            self.connection.push(("000000037ff07bfe 00 "+key+" lcdd\n").encode())
            self.connection.push(("000000037ff07bfe 01 "+key+" lcdd\n").encode())
        #except:
        #    pass

    def send(self, msg):
        self.connection.push((msg+'\n').encode())

    def write(self, msg, data=[]):
        if isinstance(msg, str):
            can_id = int(msg[1:4],16)
            can_dlc = int(msg[4])
            data = [(int(msg[n*2+5:n*2+7],16) if n < can_dlc else 0) for n in range(8)]
        elif isinstance(msg, int):
            can_id = msg
            can_dlc = len(data)
            data = [(data[n] if n < can_dlc else 0) for n in range(8)]
        else:
            print('Error!!!')
            print(msg)
            print(data)
            pass

        can_frame_fmt2 = "=IB3x8B"
        self.SCan.send(struct.pack(can_frame_fmt2, can_id, can_dlc, *data)) 

    def update_html(self):
        tempdata = []
        for key in self.temperatures:
            A = math.log(self.humidities[key] / 100) + (17.62 * self.temperatures[key] / (243.12 + self.temperatures[key]));
            Td = 243.12 * A / (17.62 - A);
            Tw = self.temperatures[key]*math.atan(0.151977*math.sqrt(self.humidities[key]+8.313659)) + math.atan(self.temperatures[key] + self.humidities[key]) - math.atan(self.humidities[key] - 1.676331) + 0.00391838*math.sqrt((self.humidities[key])**3) * math.atan(0.023101*self.humidities[key]) - 4.686035
            tempdata.append({
                    "Sensor":key,
                    "Temp":"%5.02f &deg;C"%self.temperatures[key],
                    "Humid":"%5.02f %%"%self.humidities[key],
                    "TDew":"%5.02f &deg;C"%Td,
                    "Twb":"%5.02f &deg;C"%Tw,
                    "LastUpdated":self.lastupdated[key].strftime('%H:%M:%S %a %d %b')
                    })
        json.dump(tempdata, open('/var/www/temperature/confoair.json','w'))
        tempdata=[]
        for item in sorted(self.gathereddata.items(), key=lambda kv: kv[1]):#sorted(self.gathereddata):
            tempdata.append({"measurement":item[1]})
        json.dump(tempdata, open('/var/www/temperature/confoair2.json','w'))


    def reader(self):
        """loop forever and copy serial->socket"""
        self.receivelist = []
        self.temperatures = {
                "inletbefore":10.0,
                "inletafter":10.0,
                "outletbefore":10.0,
                "outletafter":10.0,
                }
        self.humidities = {
                "inletbefore":10.0,
                "outletbefore":10.0,
                "inletafter":10.0,
                "outletafter":10.0,
                }
        self.lastupdated = {
                "inletbefore":datetime.datetime.now(),
                "outletbefore":datetime.datetime.now(),
                "inletafter":datetime.datetime.now(),
                "outletafter":datetime.datetime.now(),
                }
        
        sys.stdout.write("Starting to read the serial CANBUS input\n")
        self.gathereddata = {}

        ntouch = len(mapping.mapping)
        while True:
            try:
                if ntouch > 0:
                    ntouch -= 1
                    self.cnet.request_tdpo(list(mapping.mapping)[ntouch])

                cf, addr = self.SCan.recvfrom(16)
         
                can_id, can_dlc, data = dissect_can_frame(cf)
                #print('Received: can_id=%x, can_dlc=%x, data=%s' % dissect_can_frame(cf))
                if can_id == 0x10040001:
                    self.write(0x10140001|socket.CAN_EFF_FLAG,data)
                if can_id == 0x10000001:
                    #self.write(0x10000005|socket.CAN_EFF_FLAG, [])
                    pass
                can_str = '%08X'%can_id
                pdid = (can_id>>14)&0x7ff
                if (can_id&0x1F000000) == 0 and pdid in mapping.mapping:
                    stuff = mapping.mapping[pdid]
                    try:
                        self.gathereddata[can_str]='%s_%d %.2f %s'%(stuff["name"], (can_id>>14), stuff["transformation"](data),stuff["unit"])
                        namesplit = stuff["name"].split('_')
                        #print(namesplit)
                        if len(namesplit)>0 and namesplit[0]=="temperature":
                            key = namesplit[1]+namesplit[2]
                            self.temperatures[key]=stuff["transformation"](data)
                            self.lastupdated[key] = datetime.datetime.now()
                        elif len(namesplit)>1 and namesplit[1]=="humidity":
                            key = namesplit[2]+namesplit[3]
                            self.humidities[key]=stuff["transformation"](data)
                            self.lastupdated[key] = datetime.datetime.now()
                        elif len(namesplit)>1 and namesplit[1]=="volume":
                            self.speed == stuff["transformation"](data)


                    except:
                        print(traceback.format_exc())
                        pass
                else:
                    word = 0
                    for n in range(can_dlc):
                        word += data[n]<<(8*n)
                    self.gathereddata[can_str]='_'.join(["z--Unknown",can_str, '%d'%(can_id>>14),  ' '.join(['%X'%x for x in data]), ' ' if can_dlc<1 else '%d'%(word) ] )
                    pass
                    #print("Unknown: %s"%can_str)
                #print("\x1b[2J\x1b[H")
                for key in sorted(self.gathereddata):
                    print(self.gathereddata[key])
                    pass

                if (can_id>>8) == 0x100000:
                    self.update_html()
                
            except (socket.error):
                sys.stderr.write('ERROR in the CAN socket code somewhere...\n')
                # probably got disconnected
                break
                self.alive = False
            except:
                raise
            
    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()

touchlist = [
        0x00148068,
        0x00454068,
        0x00458068,
        0x001E0068,
        0x001DC068,
        0x001E8068,
        0x001E4068,
        0x00200068,
        0x001D4068,
        0x001D8068,
        0x0082C068,
        0x00384068,
        0x00144068,
        0x00824068,
        0x00810068,
        0x00208068,
        0x00344068,
        0x00370068,
        0x00300068,
        0x00044068,
        0x00204068,
        0x00084068,
        0x00804068,
        0x00644068,
        0x00354068,
        0x00390068,
        0x0035C068,
        0x0080C068,
        0x000E0068,
        0x00604068,
        0x00450068,
        0x00378068,
        0x00818068,
        0x00820068,
        0x001D0068,
        0x00350068,
        0x0081C068,
        0x00448068,
        0x0044C068,
        0x00560068,
        0x00374068,
        0x00808068,
        0x00040068,
        0x10040001,
        0x00120068,
        0x00688068,
        0x00358068,
        0x00104068,
        0x00544068,
        0x00814068,
        0x000C4068,
        0x00828068,
        0x00488068,
        0x0048C068,
        0x00490068,
        0x00494068,
        0x00498068,
        0x004C4068,
        0x004C8068,
        0x00388068,
        0x00188068,
        0x00184068,
        0x00108068,
        0x0038C068,
        0x00360068,
        0x00398068,
        ]

if __name__ == '__main__':
 
    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "Simple Serial to Network (TCP/IP) redirector.",
    )
    
    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages",
        default = False
    )

    parser.add_option("--spy",
        dest = "spy",
        action = "store_true",
        help = "peek at the communication and print all data to the console",
        default = False
    )
    
    parser.add_option("-s", "--socket",
        dest = "socket",
        help = "Socket to create for communication with can app",
        default = "/var/run/sockfile",
        )
    
    (options, args) = parser.parse_args()
    
    # create a raw socket and bind it to the given CAN interface
    s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    s.bind(("slcan0",))

    if options.quiet:
        stdout_logger = logging.getLogger('log')
        stdout_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
              '/tmp/can.log', maxBytes=1e6, backupCount=5)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        stdout_logger.addHandler(handler)
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        sys.stderr = sl

    r = Redirector(
            s,
            sink(),
            options.spy,
            )

    try: 
        while True:
            try:
                r.reader()
                if options.spy: sys.stdout.write('\n')
                sys.stderr.write('Disconnected\n')
                s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
                s.bind(("slcan0",))
                r.SCan = s
                #connection.close()
            except KeyboardInterrupt:
                break
            except (socket.error):
                sys.stderr.write('ERROR\n')
                sleep(1)
                #msg = input('> ')
                #msg = 'UP'    
                #time.sleep(5)
                #client.push((msg + '\n').encode())
                #client.push(b'dit is een lang verhaal\nmet terminators erin\nUP\nhoe gaat het ding hiermee om?\n')
    finally:
        pass
       
# vim: et:sw=4:ts=4:smarttab:foldmethod=indent:si
