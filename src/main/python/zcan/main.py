from multiprocessing import Process, Manager

import time

from zcan.can import CanBusReader

manager = Manager()
d = manager.dict()


def input(data):
    reader = CanBusReader()
    reader.
    CanBusReader().read_messages(data)


def output(data):
    while True:
        print(data)
        time.sleep(2)


p1 = Process(target=input, args=(d,))
p2 = Process(target=output, args=(d,))

p1.start()
p2.start()
p1.join()
p2.join()
