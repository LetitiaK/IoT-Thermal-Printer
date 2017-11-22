#!/usr/bin/python

from __future__ import print_function
import base64
import HTMLParser
import httplib
import json
import sys
import urllib
import zlib
from unidecode import unidecode
import RPi.GPIO as GPIO
from Adafruit_Thermal import *

GPIO.setmode(GPIO.BOARD)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

ledPinRed = 24    # GPIO Red
ledPinGreen = 26    # GPIO Green

# Twitter application credentials
consumer_key = '[YOUR CONSUMER KEY]'
consumer_secret = '[YOUR CONSUMER SECRET]'

# queryString
queryString = '[YOUR QUERY STRING]'

# Other globals
printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
host = 'api.twitter.com'
authUrl = '/oauth2/token'
searchUrl = '/1.1/search/tweets.json?'
agent = 'Gutenbird v1.0'

# lastID is command line value (if passed), else 1
if len(sys.argv) > 1:
    lastId = sys.argv[1]
else:
    lastId = '1'


# Initiate an HTTPS connection/request, uncompress and JSON-decode results
def issueRequestAndDecodeResponse(method, url, body, headers):
    connection = httplib.HTTPSConnection(host)
    connection.request(method, url, body, headers)
    response = connection.getresponse()
    if response.status != 200:
        # This is OK for command-line testing, otherwise
        # keep it commented out when using main.py
        # print('HTTP error: %d' % response.status)
        exit(-1)
    compressed = response.read()
    connection.close()
    return json.loads(zlib.decompress(compressed, 16+zlib.MAX_WBITS))


token = issueRequestAndDecodeResponse(
  'POST', authUrl, 'grant_type=client_credentials',
  {'Host': host,
   'User-Agent': agent,
   'Accept-Encoding': 'gzip',
   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
   'Authorization': 'Basic ' + base64.b64encode(
     urllib.quote(consumer_key) + ':' + urllib.quote(consumer_secret))}
  )['access_token']


# Perform search

data = issueRequestAndDecodeResponse(
  'GET',
  (searchUrl + 'count=3&since_id=%s&q=%s' %
   (lastId, urllib.quote(queryString))),
  None,
  {'Host': host,
   'User-Agent': agent,
   'Accept-Encoding': 'gzip',
   'Authorization': 'Bearer ' + token})


# Display results.


maxId = data['search_metadata']['max_id_str']

for tweet in data['statuses']:

    GPIO.output(ledPinGreen, GPIO.HIGH)

    printer.inverseOn()
    printer.print(' ' + '{:<31}'.format(tweet['user']['screen_name']))
    printer.inverseOff()

    printer.underlineOn()
    printer.print('{:<32}'.format(tweet['created_at']))
    printer.underlineOff()

    # max_id_str is not always present, so check tweet IDs as fallback
    id = tweet['id_str']
    if(id > maxId):
        maxId = id  # String compare is OK for this

    # Remove HTML escape sequences
    # and remap Unicode values to nearest ASCII equivalents
    printer.print(unidecode(
        HTMLParser.HTMLParser().unescape(tweet['text'])))

    GPIO.output(ledPinGreen, GPIO.LOW)

    printer.feed(3)

print(maxId)  # Piped back to calling process
