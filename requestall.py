#!/usr/bin/python3
import mapping2,os
for i in (map(lambda x:(x<<14)+0x41, mapping2.mapping.keys())):
  cmd = "/usr/bin/cansend can1 %08x#R" %i
  print(cmd)
  os.system(cmd)
