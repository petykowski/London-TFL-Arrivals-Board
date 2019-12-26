import config
from constant import *
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

url = 'https://api.tfl.gov.uk/Line/district,hammersmith-city/Arrivals/940GZZLUWPL'
payload = {'app_id': config.app_id, 'app_key': config.app_key, 'direction': 'inbound'}


class trainArrival:
  '''
  Represents an arriving train for the given station and direction.
  '''

  def __init__(self, item):
    self.id = item['id']
    self.timeOfExpiration = item['timeToStation'] + 60
    self.timeOfExpectedArrival = time.time() + item['timeToStation']
    self.timeToStation = item['timeToStation']
    self.destinationName = item['towards']


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
          "timeToStation" : 684,
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


def setDisplayStyle(style=STYLE_OLD):
  '''
  Returns the appropriate fonts for the given display style.
  NOTE: All style options can be found in the file, constant.py
  '''

  if style == STYLE_OLD:
    font_regular = generate_Font('London Underground Regular.ttf', 9)
    font_bold = generate_Font('London Underground Bold.ttf', 9)
  else:
    font_regular = generate_Font('Dot Matrix Regular.ttf', 9)
    font_bold = generate_Font('Dot Matrix Bold.ttf', 9)

  return font_regular, font_bold


def build_arrival_time(display, timeToStation, row_num):
  '''
  Returns the time component for the arriving train. This function
  accepts an integer 'timeToStation' (in seconds) which represents
  the arrival time for the given train.
  '''

  timeToStation = timeToStation - time.time()
  arrival_time = ''
  arrival_text = ''

  if timeToStation >= 60:
    # Round up to the next minute
    arrival_time = str(math.ceil(timeToStation/60))
    arrival_text = ' mins'
  elif timeToStation < 60 and timeToStation > 30:
    # Round up to 1 minute
    arrival_time = str(math.ceil(timeToStation/60))
    arrival_text = ' min'
  else:
    # Return an empty string indicating that train is due
    arrival_text = ''

  w_time, h_time = display.textsize(arrival_time, font_regular)
  w_text, h_text = display.textsize(' mins', font_regular)

  display.text((DISPLAY_WIDTH-(w_time + w_text), ((row_num-1) * 14)), text=arrival_time + arrival_text, font=font_regular, fill="yellow")


def build_clock(display):
  '''
  Returns a clock which displays the current time . This function 
  will only return a colon ":" between the time numbers every 
  half second.
  '''

  current_time_local = time.localtime()
  current_time_milli = current_milli_time()

  if current_time_milli > 500:
    current_time = time.strftime("%H:%M:%S", current_time_local)
  else:
    current_time = time.strftime("%H %M %S", current_time_local)

  w1, h1 = display.textsize(current_time, font_bold)
  display.text((((DISPLAY_WIDTH-w1)/2), (DISPLAY_HEIGHT-h1)), text=current_time, font=font_bold, fill="yellow")


def generate_arrival_row(display, arrival, row_num):
  display.text((0, ((row_num-1) * 14)), text=str(row_num), font=font_regular, fill="yellow")
  display.text((10, ((row_num-1) * 14)), text=arrival.destinationName, font=font_regular, fill="yellow")
  build_arrival_time(display, arrival.timeOfExpectedArrival, row_num)


def generate_departure_board(device, data):

  if not data:
    with canvas(device) as display:
      display.text((0, 0), text="Welcome to Aldgate East Station", font=font_regular, fill="yellow")
      display.text(((DISPLAY_WIDTH/2), (DISPLAY_HEIGHT-14)), text=current_time, font=font_regular, fill="yellow")
  else:
    row_num = 0
    with canvas(device) as display:

      for arrival in data:
        row_num += 1
        generate_arrival_row(display, arrival, row_num)

      # Generate Time
      build_clock(display)


def generate_Font(name, size):
  '''
  Returns an ImageFont for use when displaying text on the device.
  '''

  font_path = os.path.abspath(
      os.path.join(
          os.path.abspath(__file__ + "/../../assets/"),
          "fonts",
          name
      )
  )
  return ImageFont.truetype(font_path, size)


try:
  current_milli_time = lambda: int(str(round(time.time() * 1000))[-3:])
  is_train_approaching = False
  upcoming_arrivals = []

  font_regular, font_bold = setDisplayStyle()

  last_refresh_time = time.time() - REFRESH_INTERVAL

  device = get_device()

  while True:

    # Refresh Data when TTL Expired
    if (time.time() - last_refresh_time >= REFRESH_INTERVAL):

      json = query_TFL(url, payload)
      sortedJson = sorted(json, key=lambda k: k['timeToStation'])
      upcoming_arrivals = []

      for departure in sortedJson:
        upcoming_arrivals.append(trainArrival(departure))

      last_refresh_time = time.time()

    generate_departure_board(device, upcoming_arrivals[:3])
    time.sleep(.1)


except KeyboardInterrupt:
  pass

except ValueError as e:
  print(e)

except Exception as e:
  raise e