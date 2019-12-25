import config
import constant
from helper import get_device
from PIL import ImageFont, Image
import requests
import json
import time
import os
import sys
import math
from luma.core.render import canvas
# from luma.core.virtual import viewport, snapshot

url = 'https://api.tfl.gov.uk/Line/central/Arrivals/940GZZLULVT'
payload = {'app_id': config.app_id, 'app_key': config.app_key, 'direction': 'inbound'}


class trainArrival:

    def __init__(self, item):
      self.id = item['id']
      self.timeOfExpiration = item['timeToStation'] + 60
      self.timeOfExpectedArrival = time.time() + item['timeToStation']
      self.timeToStation = item['timeToStation']
      self.destinationName = item['destinationName']


def query_TFL(url, params):
  response = requests.get(url, params=params)
  if response.status_code == 200:
    if not response.json():
      debug_while_down = [
        {
          "id" : 1,
          "timeToStation" : 45,
          "destinationName" : 'Wimbledon Underground Station'
        },
        {
          "id" : 2,
          "timeToStation" : 125,
          "destinationName" : 'Richmond Underground Station'
        },
        {
          "id" : 3,
          "timeToStation" : 448,
          "destinationName" : 'Ealing Broadway Underground Station'
        }
      ]
      print('Nothing was returned from TFL')
      return debug_while_down
    else:
      print('Success. Returning JSON')
      return response.json()
  else:
    raise ValueError('Error Communicating with TFL')


def format_time_component(timeToStation):
  # Returns the time component for the arriving train. This function
  # accepts an integer 'timeToStation' (in seconds) which represents
  # the arrival time for the given train.

  if timeToStation >= 60:
    # Round up to the next minute
    return str(math.ceil(timeToStation/60)) + ' mins'
  elif timeToStation < 60 and timeToStation > 30:
    # Round up to 1 minute
    return str(math.ceil(timeToStation/60)) + ' min'
  else:
    # Return an empty string indicating that train is due
    is_train_approaching = True
    return ''


def format_destination_component(destinationName):
  return destinationName[0:-20]

def generate_current_time(display, width, height):
  # This function will only return a colon ":"
  # between the time numbers every other second
  # TODO: The actual departure board will flash colons every half second.
  t = time.localtime()

  if current_milli_time() > 500:
    current_time = time.strftime("%H:%M:%S", t)
  else:
    current_time = time.strftime("%H %M %S", t)
  display.text((((width-constant.DISPLAY_TIME_WIDTH)/2), (height-constant.DISPLAY_TIME_HEIGHT)), text=current_time, font=font_bold, fill="yellow")


def generate_arrival_row(display, arrival, row_num):
  global scroll_index
  scroll_index += 1
  display.text((0, ((row_num-1) * 14)), text=str(row_num), font=font_regular, fill="yellow")
  display.text((14, ((row_num-1) * 14)), text=format_destination_component(arrival.destinationName), font=font_regular, fill="yellow")
  w1, h1 = display.textsize(format_time_component(arrival.timeOfExpectedArrival - time.time()), font_regular)
  display.text((displayWidth - 46, ((row_num-1) * 14)), text=format_time_component(arrival.timeOfExpectedArrival - time.time()), font=font_regular, fill="yellow")

def generate_departure_board(device, width, height, data):

  if not data:
    with canvas(device) as display:
      display.text((0, 0), text="Welcome to Aldgate East Station", font=font_regular, fill="yellow")
      display.text(((width/2), (height-14)), text=current_time, font=font_regular, fill="yellow")
  else:
    row_num = 0
    with canvas(device) as display:

      for arrival in data:
        row_num += 1
        generate_arrival_row(display, arrival, row_num)

      # Generate Time
      generate_current_time(display, width, height)


def makeFont(name, size):
  font_path = os.path.abspath(
      os.path.join(
          os.path.abspath(__file__ + "/../../assets/"),
          "fonts",
          name
      )
  )
  return ImageFont.truetype(font_path, size)


try:
  global displayWidth, displayHeight, is_train_approaching, current_milli_time, scroll_index
  scroll_index = 1
  current_milli_time = lambda: int(str(round(time.time() * 1000))[-3:])
  displayWidth = 256
  displayHeight = 64
  is_train_approaching = False
  upcoming_arrivals = []
  font_regular = makeFont('London Underground Regular.ttf', 9)
  font_bold = makeFont('London Underground Bold.ttf', 9)
  last_refresh_time = time.time() - constant.REFRESH_INTERVAL

  device = get_device()

  while True:

    # Refresh Data when TTL Expired
    if (time.time() - last_refresh_time >= constant.REFRESH_INTERVAL):

      json = query_TFL(url, payload)
      sortedJson = sorted(json, key=lambda k: k['timeToStation'])
      upcoming_arrivals = []

      for departure in sortedJson:
        upcoming_arrivals.append(trainArrival(departure))

      last_refresh_time = time.time()

    generate_departure_board(device, displayWidth, displayHeight, upcoming_arrivals[:3])
    time.sleep(.1)


except KeyboardInterrupt:
  pass

except ValueError as e:
  print(e)

except Exception as e:
  raise e