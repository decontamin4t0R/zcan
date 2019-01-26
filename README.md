# zcan

Although this is a fork from the great work of marco-hoyer, the goal for this repository is quite different. My goal is to create a set of python scripts to monitor and actively control the ComfoAirQ units.

## Status
Mapping is quite complete, commands still need a lot of work.

Also there is no build system or anything, for now just a bunch of scripts.

ComfoNetCan.py: class to translate between CAN encoded messages to ComfoNet and back

Mapping2.py: list of pdo items and their meaning

Sendmsg.py: Example of how to send a message over the ComfoNet

Testcan.py: Example of monitoring ComfoNet pdo/pdo messages and write to json files (for showing in a html page)

Zcanbridge.py: Transfer the RhT value to my DeCONZ REST API
