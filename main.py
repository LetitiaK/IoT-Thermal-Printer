from __future__ import print_function
import os
import RPi.GPIO as GPIO
import subprocess
import time
import Image
import socket
from Adafruit_Thermal import *


# Button connections
GPIO.setmode(GPIO.BOARD)
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

ledPinRed = 24    # GPIO Red
ledPinGreen = 26    # GPIO Green
buttonPin = 23    # GPIO for the button
tapTime = 0.01  # Debounce time for button taps
holdTime = 2     # Duration for button hold (shutdown)
lastId = '1'   # State information passed to/from interval script
dailyFlag = False  # Set after daily trigger occurs
nextInterval = 0.0   # Interval for Twitter Check
printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)


# Called when button is briefly tapped.  Invokes the yahoo! weather script.
def tap():
    GPIO.output(ledPinGreen, GPIO.HIGH)
    GPIO.output(ledPinRed, GPIO.LOW)
    subprocess.call(["python", "fortune.py"])
    subprocess.call(["python", "sudoku-gfx.py"])
    GPIO.output(ledPinRed, GPIO.HIGH)
    GPIO.output(ledPinGreen, GPIO.LOW)


# Called when button is held down.  Prints image, invokes shutdown process.
def hold():
    GPIO.output(ledPinGreen, GPIO.LOW)
    GPIO.output(ledPinRed, GPIO.HIGH)
    printer.print ("Bye bye! Have a nice day :)")
    printer.printImage(Image.open('gfx/goodbye.png'), True)
    printer.feed(3)
    subprocess.call("sync")
    subprocess.call(["shutdown", "-h", "now"])


# Called at periodic intervals (30 seconds by default).
# Invokes twitter script.
def interval():
    GPIO.output(ledPinGreen, GPIO.HIGH)
    GPIO.output(ledPinRed, GPIO.LOW)
    p = subprocess.Popen(["python", "twitter.py", str(lastId)],
                         stdout=subprocess.PIPE)
    GPIO.output(ledPinGreen, GPIO.LOW)
    return p.communicate()[0]  # Script pipes back lastId, return to gpiobutton


# Called once per day.
# Invokes weather forecast and sudoku-gfx scripts.
def daily():
    subprocess.call(["python", "yahoofc.py"])


# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting.
GPIO.output(ledPinGreen, GPIO.LOW)
GPIO.output(ledPinRed, GPIO.HIGH)
time.sleep(30)
GPIO.output(ledPinGreen, GPIO.HIGH)
GPIO.output(ledPinRed, GPIO.LOW)
time.sleep(2)
GPIO.output(ledPinGreen, GPIO.LOW)

# Poll inital button state and time
prevButtonState = GPIO.input(23)
prevTime = time.time()
tapEnable = False
holdEnable = False

# Main loop
while(True):

    # Poll current button state and time
    buttonState = GPIO.input(buttonPin)
    t = time.time()

    # Has button state changed?
    if buttonState != prevButtonState:
        prevButtonState = buttonState   # Yes, save new state/time
        prevTime = t
    else:                             # Button state unchanged
        if (t - prevTime) >= holdTime:  # Button held more than 'holdTime'?
            if holdEnable:
                hold()                      # Perform hold action
                holdEnable = False          # 1 shot...don't repeat hold action
                tapEnable = False          # Don't do tap action on release
        if (t - prevTime) >= tapTime:  # Not holdTime.  tapTime elapsed?
            if buttonState:       # Button released?
                if tapEnable:       # Ignore if prior hold()
                    tap()                     # Tap triggered (button released)
                    tapEnable = False        # Disable tap and hold
                    holdEnable = False
            else:                         # Button pressed
                tapEnable = True           # Enable tap and hold actions
                holdEnable = True

    # Once per day (currently set for 08:30am local time, or when script
    # is first run, if after 08:30am), run yahoo forecast script.
    l = time.localtime()
    if (60 * l.tm_hour + l.tm_min) > (60 * 8 + 30):
        if dailyFlag is False:
            daily()
            dailyFlag = True
        else:
            dailyFlag = False  # Reset daily trigger

    # Every 30 seconds, run Twitter scripts.  'lastId' is passed around
    # to preserve state between invocations.
    if t > nextInterval:
        nextInterval = t + 30.0
        result = interval()
    if result is not None:
        lastId = result.rstrip('\r\n')
