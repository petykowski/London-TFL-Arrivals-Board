import config
import constant
import requests
import json
import time

url = 'https://api.tfl.gov.uk/Line/district/Arrivals/940GZZLUADE'
payload = {'app_id': config.app_id, 'app_key': config.app_key, 'direction': 'inbound'}


class trainDeparture:

    def __init__(self, item):
      self.id = item['id']
      self.timeToStation = item['timeToStation']
      self.destinationName = item['destinationName']


def query_TFL(url, params):
  response = requests.get(url, params=params)
  if response.status_code == 200:
    return response.json()
  else:
    raise ValueError('Error Communicating with TFL')


def format_time_component(timeToStation):
  if timeToStation >= 90:
    return str(round(timeToStation/60)) + ' mins'
  elif timeToStation <= 90 and timeToStation > 30:
    return str(round(timeToStation/60)) + ' min'
  else:
    return 'due'


def format_destination_component(destinationName):
  return destinationName[0:-20]


def generate_departure_board():
  t = time.localtime()
  current_time = time.strftime("%H %M %S", t)
  print(format_destination_component(upcoming_departures[0].destinationName))
  print(format_time_component(upcoming_departures[0].timeToStation))
  print(constant.MSG_TRAIN_APPROACHING)
  print(current_time)


try:
  json = query_TFL(url, payload)
  sortedJson = sorted(json, key=lambda k: k['timeToStation'])
  upcoming_departures = []
  for departure in sortedJson:
    upcoming_departures.append(trainDeparture(departure))
  generate_departure_board()

except ValueError as e:
  print(e)

except Exception as e:
  raise e