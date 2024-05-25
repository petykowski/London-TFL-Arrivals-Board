# London TfL Arrivals Board

Miniature Python-based TfL Arrivals Board Running via Raspberry Pi Zero W

![](assets/img/train-approaching.gif)

## Project Details
I created a thread on Twitter with a video of the arrivals board in action, along with some additional details on how I created it.

[Twitter - TfL Arrival Board Thread ](https://twitter.com/petykowski_/status/1251173895547359234) 

## Configuration
London TfL Arrivals Board will display upcoming Tube and DLR train arrivals based on the configured station. Each station on the network has 2 directions of travel, inbound and outbound.

_Please note: certain stations have multiple platforms which can cause unexpected behaviour._

London TfL Arrivals Board allows for stations to be configured manually, via constants, or automatically by referencing a remote file. Regardless of configuration option, a `config.py` file is always required.

**config.py**

A `config.py` file is required in order to run London TfL Arrivals Board. Please review the `config_example.py` file for further details on the required details. Copy `src/config_example.py` to `src/config.py` and populate the values as needed.

```python
app_id = '1a2b3c4d' # TfL API no longer requires an app_id, acceptable to populate with dummy value.
app_key = '1a2b3c4d5e6f7g8h9i'
station_url = 'https://url.to.remote.station.file.com/station.txt'
``` 

### Manual Configuration
Manual configuration allows users to directly hardcode the station name, travel mode, and direction. These values are then referenced by London TfL Arrivals Board to look up and then display the upcoming arrivals.

**constant.py**

To manually configure the station that will be displayed on London TfL Arrivals Board, you will need to populate 3 values in the `constant.py` file; `TRAVEL_MODE`, `STATION_NAME`, and `DIRECTION`.

Start by uncommenting out `STATION_NAME`, and `DIRECTION` values and then populate with the desired values. `STATION_NAME` accepts a TfL station name and `DIRECTION` accepts 'inbound' or 'outbound'.

_Please Note: Other values in the `constant.py` file do not require modification unless you need to adjust your display size, customising the "Not in Service" message or would like to change the font style that is uesd. Please do not modify these values unless you know what you are doing._

```python
TRAVEL_MODE = 'tube' # Supported options 'tube' or 'dlr'
STATION_NAME = 'Canary Wharf'
DIRECTION = 'inbound' # Supported options 'inbound' or 'outbound'
```

### Remote Configuration
Remote configuration provides you with more options to dynamically update the station displayed on London TfL Arrivals Board via a Siri Shortcut, API call, or via a webpage.

**station.txt**

`station.txt` is a externally hosted file which contains 3 parameters related to the TfL station which is to be displayed on the arrivals board. The arrivals board will periodically pull this file, compare the `updated_on` parameter, and refresh the station as required. An example of the file contents is as follows:
```json
{
  "station": "Seven Sisters",
  "direction": "Inbound",
  "updated_on": "2022-06-20T23:45:16+01:00"
}
``` 

## Looking for the Typeface?
Check out my [London Underground Dot Matrix Typeface](https://github.com/petykowski/London-Underground-Dot-Matrix-Typeface) repository to download the dot matrix typeface used in this project.

## Inspiration
* Chris Hutchinson's [UK Train Departure Screen](https://github.com/chrishutchinson/train-departure-screen)
* [UK Departure Boards](https://ukdepartureboards.co.uk/) via [Geoff Marshall](https://www.youtube.com/watch?v=EgLGKjj3GwI)

## Attributions
Powered by [TfL Open Data](https://api.tfl.gov.uk)
* Contains OS data © Crown copyright and database rights [2016]
* Geomni UK Map data © and database rights [2019]

Additional Dot Matrix Font by [Daniel Hart](https://github.com/DanielHartUK/Dot-Matrix-Typeface)