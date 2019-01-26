#!/bin/python3
import struct
import socket


cmdMapping = {
        "NODE": 0x1,
        "COMFOBUS": 0x2,
        "ERROR": 0x3,
        "SCHEDULE": 0x15,
        "VALVE": 0x16,
        "FAN": 0x17,
        "POWERSENSOR": 0x18,
        "PREHEATER": 0x19,
        "HMI": 0x1A,
        "RFCOMMUNICATION": 0x1B,
        "FILTER": 0x1C,
        "TEMPHUMCONTROL": 0x1D,
        "VENTILATIONCONFIG": 0x1E,
        "NODECONFIGURATION": 0x20,
        "TEMPERATURESENSOR": 0x21,
        "HUMIDITYSENSOR": 0x22,
        "PRESSURESENSOR": 0x23,
        "PERIPHERALS": 0x24,
        "ANALOGINPUT": 0x25,
        "COOKERHOOD": 0x26,
        "POSTHEATER": 0x27,
        "COMFOFOND": 0x28,
        "COOLER": 0x15,
        "CC_TEMPERATURESENSOR": 0x16,
        "IOSENSOR": 0x15,
        }

cmdSchedules = {
        "GETSCHEDULEENTRY": 0x80,
        "ENABLESCHEDULEENTRY": 0x81,
        "DISABLESCHEDULEENTRY": 0x82,
        "GETTIMERENTRY": 0x83,
        "ENABLETIMERENTRY": 0x84,
        "DISABLETIMERENTRY": 0x85,
        "GETSCHEDULE": 0x86,
        "GETTIMERS": 0x87,
        }

class CN1FAddr:
    def __init__(self, SrcAddr, DstAddr, Address, MultiMsg, A8000, A10000, SeqNr):
        self.SrcAddr = SrcAddr
        self.DstAddr = DstAddr
        self.Address = Address
        self.MultiMsg = MultiMsg
        self.A8000 = A8000
        self.A10000 = A10000
        self.SeqNr = SeqNr

    @classmethod
    def fromCanID(cls, CID):
        if (CID>>24) != 0x1F:
            raise ValueError('Not 0x1F CMD!')
        else:
            return cls(
                (CID>> 0)&0x3f,
                (CID>> 6)&0x3f,
                (CID>>12)&0x03,
                (CID>>14)&0x01,
                (CID>>15)&0x01,
                (CID>>16)&0x01,
                (CID>>17)&0x03)
                
    def __repr__(self):
        return (f'{self.__class__.__name__}(\n'
            f'  SrcAddr = {self.SrcAddr:#02x},\n'
            f'  DstAddr = {self.DstAddr:#02x},\n'
            f'  Address = {self.Address:#02x},\n'
            f'  MultiMsg = {self.MultiMsg:#02x},\n'
            f'  A8000 = {self.A8000:#02x},\n'
            f'  A10000 = {self.A10000:#02x},\n'
            f'  SeqNr = {self.SeqNr:#02x})')

    def CanID(self):
        addr = 0x0
        addr |= self.SrcAddr << 0
        addr |= self.DstAddr << 6
        
        addr |= self.Address <<12
        addr |= self.MultiMsg<<14
        addr |= self.A8000   <<15
        addr |= self.A10000  <<16
        addr |= self.SeqNr   <<17
        addr |= 0x1F         <<24
        
        return addr

class ComfoNet:
    def __init__(self, cansocket):
        self.Seq = 0
        self.can = cansocket

    def write_CN_Msg(self, SrcAddr, DstAddr, C3000, C8000, C10000, data):
        A = CN1FAddr(SrcAddr, DstAddr, C3000, len(data)>8, C8000, C10000, self.Seq)
        
        self.Seq = (self.Seq + 1)&0x3

        if len(data) > 8:
            datagrams = int(len(data)/7)
            if len(data) == datagrams*7:
                datagrams -= 1
            for n in range(datagrams):
                self.canwrite(A.CanID(), [n]+data[n*7:n*7+7])
            n+=1
            restlen = len(data)-n*7
            self.canwrite(A.CanID(), [n|0x80]+data[n*7:n*7+restlen])
        else:
            self.canwrite(A.CanID(), data)

    def request_tdpo(self, DpoID):
        cid = (DpoID<<14)|0x01<<6|self.ComfoAddr|socket.CAN_EFF_FLAG|socket.CAN_RTR_FLAG
        print("0x%8X"%(cid))
        self.can.send(struct.pack("=IB3x8B", cid,0,*[0]*8))

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = struct.unpack("=IB3x8s", frame)
        if can_id & socket.CAN_RTR_FLAG != 0:
            print("RTR received from %08X"%(can_id&socket.CAN_EFF_MASK))
            return(0,0,[])
        can_id &= socket.CAN_EFF_MASK
        
        return (can_id, can_dlc, data[:can_dlc])
    
    def canwrite(self, msg, data=[]):
        print(('%X#'+'%02X'*len(data))%((msg,)+tuple(data)))
        can_id = msg | socket.CAN_EFF_FLAG
        can_dlc = len(data)
        data = [(data[n] if n < can_dlc else 0) for n in range(8)]

        #print(msg)
        #print(data)
        self.can.send(struct.pack("=IB3x8B", can_id, can_dlc, *data)) 

    def FindComfoAirQ(self):
        while True:
            cf, addr = self.can.recvfrom(16)
         
            can_id, can_dlc, data = self.dissect_can_frame(cf)
            print('Received: can_id=%x, can_dlc=%x, data=%s' % self.dissect_can_frame(cf))
            if can_id & 0xFFFFFFC0 == 0x10000000:
                self.ComfoAddr = can_id&0x3f
                print(f'{self.ComfoAddr:#06X}')
                break

    def ShowReplies(self):
        for n in range(100):
            cf, addr = self.can.recvfrom(16)
         
            can_id, can_dlc, data = self.dissect_can_frame(cf)
            if can_id & 0x1F000000 == 0x1F000000:
                print(f'Reply: {can_id:#06X} ' + ":".join(f'{c:02x}' for c in data ))

    def ConvertCN1FCmds(self):
        while True:
            cf, addr = self.SCan.recvfrom(16)
         
            can_id, can_dlc, data = dissect_can_frame(cf)
            print('Received: can_id=%x, can_dlc=%x, data=%s' % dissect_can_frame(cf))
            try:
                CNAddr = CN1FAddr.fromCanID(can_id)
            except ValueError:
                pass

            if self.CN.SrcAddr:
                pass

    def DecodeCanID(self, canID):
        pass

def msgclass():
    data =[
            0x84, #CmdID
            0x15, #ItemInLookupTable
            0x01, #Type --> selects field1 or field2... if that field is 1, OK
            #Start actual command... 
            0x01, #FF special case, otherwise -1 selects timer to use..?SubCMD?
            0x00, 0x00, 0x00, 0x00, #v9
            0x00, 0x1C, 0x00, 0x00, #v10
            0x03, #v11 Check vs type-1 0: <=3, 1,2,9:<=2, 3,4,5,6,7,8<=1
            0x00,
            0x00,
            0x00]


# vim:ts=4:sw=4:si:et:fdm=indent:
