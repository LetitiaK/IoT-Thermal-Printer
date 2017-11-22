from __future__ import print_function
import urllib2, urllib, json
import time
import RPi.GPIO as GPIO
from Adafruit_Thermal import *

GPIO.setmode(GPIO.BOARD)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

ledPinGreen = 26
ledPinRed = 24

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

GPIO.output(ledPinGreen, GPIO.HIGH)
GPIO.output(ledPinRed, GPIO.LOW)

printer.print ("\nHello, Lilly!\nHere is your weather forecast\nfor Vienna:")

baseurl = "https://query.yahooapis.com/v1/public/yql?"

y3ql_query = "select lastBuildDate from weather.forecast where woeid=551801"
y3ql_url = baseurl + urllib.urlencode({'q': y3ql_query}) + "&format=json"
result3 = urllib2.urlopen(y3ql_url).read()
data3 = json.loads(result3)
date = data3['query']['results']['channel']['lastBuildDate']
printer.print ("\nIt is " + date)

yql_query = "select item.condition.temp from weather.forecast where woeid=551801 and u='c'"  # NOQA
yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
result = urllib2.urlopen(yql_url).read()
data = json.loads(result)
temp = data['query']['results']['channel']['item']['condition']['temp']
if temp < "22":
    printer.print ("\nTake a jacket,\nit's only " + temp + "C.")
else:
    printer.print ("\nCurrently you don't need a jacket\n cause it's " + temp + "C.")  # NOQA

y2ql_query = "select item.condition.text from weather.forecast where woeid=551801"  # NOQA
y2ql_url = baseurl + urllib.urlencode({'q': y2ql_query}) + "&format=json"
result2 = urllib2.urlopen(y2ql_url).read()
data2 = json.loads(result2)
text = data2['query']['results']['channel']['item']['condition']['text']

dayTime = False
ti = time.localtime()
if (60 * ti.tm_hour + ti.tm_min) > (60 * 6 + 30) and (60 * ti.tm_hour + ti.tm_min) < (60 * 20 + 30):  # NOQA
    dayTime = True
else:
    dayTime = False

if dayTime == True and text == "Cloudy" or text == "Mostly Cloudy" or text == "Partly Cloudy":  # NOQA
    printer.print ("\nYou won't need your sunglasses \ncause it's cloudy.")
elif dayTime == False and text == "Cloudy" or text == "Mostly Cloudy" or text == "Partly Cloudy":  # NOQA
    printer.print ("\nNo chance to see stars tonight - too cloudy :(!")
elif text == "Severe Thunderstorms" or text == "Thunderstorms" or text == "Thundershowers" or text == "Isolated Thunderstorms" or text == "Scattered Thunderstorms":  # NOQA
    printer.print ("\nBe aware, there are thunderstorms in your region!")
elif text == "Sunny" or text == "Fair (day)":
    printer.print ("\nTake your sunglasses, it's gonna be a nice day!")
elif text == "Snow" or text == "Heavy Snow" or text == "Snow Flurries" or text == "Light Snow Showers" or text == "Blowing Snow":  # NOQA
    printer.print ("\n***Let it snow, let it snow, let it snow***")
elif text == "Hail" or text == "Mixed Rain And Hail":
    printer.print ("\nWatch out! Hail today!")
elif text == "Sleet" or text == "Snow Showers" or text == "Scattered Snow Showers" or text == "Mixed Rain And Snow" or text == "Mixed Rain And Sleet" or text == "Mixed Snow And Sleet" or text == "Freezing Drizzle" or text == "Freezing Rain":  # NOQA
    printer.print ("\nWear warm wellingtons today - awful rain and snow mix today")  # NOQA
elif text == "Foggy" or text == "Haze" or text == "Smoky":
    printer.print ("\nOptimal conditions for a cloak-and dagger operation")
elif text == "Blustery" or text == "Windy":
    printer.print ("\nWear a pony tail today - it's gonna be windy!")
elif text == "Cold":
    printer.print ("\nTuck yourself up! It's freezing outside")
elif text == "Clear":
    printer.print ("\nIdeal conditions to see the stars!")
elif text == "Hot":
    printer.print ("\nHot, hot summer! Hot, hot summer!")
elif text == "Scattered Showers" or text == "Drizzle" or text == "Showers" or text == "Rain":  # NOQA
    printer.print ("\nTake an umbrella!")
elif text == "Tornado":
    printer.print ("\nWarning: Tornado!")
    GPIO.output(ledPinGreen, GPIO.LOW)

printer.feed(3)
