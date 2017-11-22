from __future__ import print_function
from time import sleep
import os
from Adafruit_Thermal import *

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

printer.print("Quote of the day: \n")

os.system("/usr/games/fortune -s definitions | python test.py")
printer.feed(1)
