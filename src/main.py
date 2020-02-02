import os
import sys
import math
import json
import time
import config
import requests
from constant import *
from pytz import timezone
from datetime import datetime
from helper import get_device
from PIL import ImageFont, Image
from luma.core.render import canvas


class undergroundStation:
  '''
  Represents a Station on the TFL Underground network.
  '''

  def __init__(self, item):
    self.userQuery = item['station']
    self.availableLines = []
    if item['direction'].lower() in [TRAVEL_DIRECTION_INBOUND, TRAVEL_DIRECTION_OUTBOUND]:
      self.direction = item['direction'].lower()
    else:
      self.direction = TRAVEL_DIRECTION_INBOUND
    self.requestedOn = item['updated_on']

  def addTFLStationData(self, item):
    self.id = item['matches'][0]['id']
    self.stationName = item['matches'][0]['name']

  def addAvailableLines(self, lines):
    self.availableLines = lines


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
    self.isTrainApproaching = item['timeToStation'] < 30


def internet_connection_found():
  '''
  Returns a boolean to determine if there is an active internet 
  connection.
  '''

  url = CHECK_INTERNET_URL
  timeout = 1

  try:
    _ = requests.get(url, timeout =timeout)
    return True

  except requests.ConnectionError:
    print("No Internet connection found")
    return False


def query_TFL(url, params):
  '''
  Wrapper function for querying the TFL API
  '''

  for retry_count in range(0,2):
    try:
      response = requests.get(url, params=params)
      if response.status_code == 200:
        if not response.json():
          print('Nothing was returned from TFL')
        else:
          print('Success. Returning JSON')
        return response.json()
      else:
        raise ValueError('Error Communicating with TFL')
    except ValueError:
      if retry_count == 2:
        raise ValueError('Max Retries Attempted')
      else:
        continue


def get_station():
  '''
  Returns a populated undergroundStation class object based on the 
  requested station name.
  '''

  response = requests.get(config.station_url)
  response_json = json.loads(response.text)
  station = undergroundStation(response_json)

  query_station_url = 'https://api.tfl.gov.uk/StopPoint/Search'
  query_station_payload = {'query': station.userQuery, 'modes': 'tube', 'app_id': config.app_id, 'app_key': config.app_key}
  station_response = query_TFL(query_station_url, query_station_payload)

  if not station_response['matches']:
    return station

  station.addTFLStationData(station_response)

  query_lines_url = 'https://api.tfl.gov.uk/StopPoint/ServiceTypes'
  query_lines_payload = {'id': station.id, 'app_id': config.app_id, 'app_key': config.app_key}
  lines_response = query_TFL(query_lines_url, query_lines_payload)

  available_lines_at_station = []
  for line in lines_response:
    available_lines_at_station.append(line['lineName'])

  station.addAvailableLines(available_lines_at_station)

  return station


def get_last_time_station_requested():
  '''
  Returns the last time station was requested
  '''

  response = requests.get(config.station_url)
  response_json = json.loads(response.text)
  return response_json['updated_on']


def query_for_arrival_data(station):
  '''
  Returns arriving trains for given station and direction
  '''

  url = 'https://api.tfl.gov.uk/Line/' + ','.join(station.availableLines) + '/Arrivals/' + station.id
  payload = {'app_id': config.app_id, 'app_key': config.app_key, 'direction': station.direction}

  return query_TFL(url, payload)


def setDisplayStyle(style=STYLE_STANDARD):
  '''
  Returns the appropriate fonts for the given display style.
  NOTE: All style options can be found in the file, constant.py
  '''

  if style == STYLE_STANDARD:
    font_regular = generate_font('London Underground Heavy.ttf', 9)
    font_bold = generate_font('London Underground Bold.ttf', 9)
  else:
    font_regular = generate_font('Dot Matrix Regular.ttf', 9)
    font_bold = generate_font('Dot Matrix Bold.ttf', 9)

  return font_regular, font_bold


def build_arrival_time(display, arrival, row_num):
  '''
  Returns the time component for the arriving train. This function
  accepts an integer 'timeToStation' (in seconds) which represents
  the arrival time for the given train.
  '''

  timeToStation = arrival.timeOfExpectedArrival - time.time()
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


def build_arrival_message(display, row_num):
  '''
  Returns an arrival message when a train is approaching the station.
  '''

  w1, h1 = display.textsize(MSG_TRAIN_APPROACHING, font_regular)
  display.text((((DISPLAY_WIDTH-w1)/2), ((row_num-1) * 14)), text=MSG_TRAIN_APPROACHING, font=font_regular, fill="yellow")


def build_clock(display, show_seconds=True):
  '''
  Returns a clock which displays the current time . This function 
  will only return a colon ":" between the time numbers every 
  half second.
  '''

  current_time_in_london = datetime.now(timezone('Europe/London'))
  current_time_milli = current_milli_time()

  if show_seconds:
    if current_time_milli > 500:
      current_time = current_time_in_london.strftime("%H:%M:%S")
    else:
      current_time = current_time_in_london.strftime("%H %M %S")
  else:
    current_time = current_time_in_london.strftime("%H:%M")

  w1, h1 = display.textsize(current_time, font_bold)
  display.text((((DISPLAY_WIDTH-w1)/2), (DISPLAY_HEIGHT-h1)), text=current_time, font=font_bold, fill="yellow")


def generate_arrival_row(display, arrival, row_num):
  display.text((0, ((row_num-1) * 14)), text=str(row_num), font=font_regular, fill="yellow")
  display.text((10, ((row_num-1) * 14)), text=arrival.destinationName, font=font_regular, fill="yellow")
  build_arrival_time(display, arrival, row_num)


def generate_welcome_board(device, data, station):
  '''
  Displays a welcome message when there are no trains approaching 
  the station, and a Not in Service message if no internet 
  connection is found.
  '''

  if not hasattr(station, 'id'):
    welcome_msg = "Not in Service"
  else:
    welcome_msg = "Welcome to " + station.stationName

  with canvas(device) as display:
    w1, h1 = display.textsize(welcome_msg, font_regular)
    display.text((((DISPLAY_WIDTH-w1)/2), 0), text=welcome_msg, font=font_regular, fill="yellow")

    # Generate Time
    build_clock(display, False)


def generate_arrival_board(device, data, station):

  if not data:
    generate_welcome_board(device, data, station)
  else:
    row_num = 1
    with canvas(device) as display:
      for arrival in data:
        generate_arrival_row(display, arrival, row_num)

        # Indicates that the train is approaching if arrival is within 15 seconds.
        if arrival.timeOfExpectedArrival - time.time() < 15:
          arrival.isTrainApproaching = True

        row_num += 1

      if True in [arrival.isTrainApproaching for arrival in data]:
        build_arrival_message(display, row_num)

      # Generate Time
      build_clock(display)


def generate_font(name, size):
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


current_milli_time = lambda: int(str(round(time.time() * 1000))[-3:])

try:

  device = get_device()
  font_regular, font_bold = setDisplayStyle()

  # Testing Font Sizes
  while True:
    with canvas(device) as display:
      font_9 = generate_font('London Underground Heavy.ttf', 9)
      font_10 = generate_font('London Underground Heavy.ttf', 10)
      font_11 = generate_font('London Underground Heavy.ttf', 11)
      font_12 = generate_font('London Underground Heavy.ttf', 12)
      font_13 = generate_font('London Underground Heavy.ttf', 13)
      display.text((0, 0), text="1 Stratford   4 mins", font=font_9, fill="yellow")
      display.text((0, 11), text="1 Stratford   4 mins", font=font_10, fill="yellow")
      display.text((0, 22), text="1 Stratford   4 mins", font=font_11, fill="yellow")
      display.text((0, 34), text="1 Stratford   4 mins", font=font_12, fill="yellow")
      display.text((0, 47), text="1 Stratford   4 mins", font=font_13, fill="yellow")


  while not internet_connection_found():
    generate_arrival_board(device, None, None)
    time.sleep(5)

  requested_station = get_station()
  last_refresh_time_aws = time.time()

  upcoming_arrivals = []
  last_refresh_time_tfl = time.time() - REFRESH_INTERVAL_TFL


  while True:

    # Refresh Station when AWS Refresh Interval Expires 
    if (time.time() - last_refresh_time_aws >= REFRESH_INTERVAL_AWS):

      # Update Station when one has been requested
      if not requested_station.requestedOn == get_last_time_station_requested():
        requested_station = get_station()
        upcoming_arrivals = []
        force_refresh = True

      last_refresh_time_aws = time.time()

    if hasattr(requested_station, 'id'):

      # Refresh Data when TTL Expired
      if (time.time() - last_refresh_time_tfl >= REFRESH_INTERVAL_TFL) or force_refresh:

        arrival_data = query_for_arrival_data(requested_station)
        arrivals_by_arrival_time = sorted(arrival_data, key=lambda k: k['timeToStation'])
        upcoming_arrivals = []

        for arriving_train in arrivals_by_arrival_time:
          upcoming_arrivals.append(trainArrival(arriving_train))

        force_refresh = False
        last_refresh_time_tfl = time.time()

    generate_arrival_board(device, upcoming_arrivals[:3], requested_station)
    time.sleep(.1)


except KeyboardInterrupt:
  pass

except ValueError as e:
  print(e)

except Exception as e:
  raise e