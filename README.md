# London TfL Arrivals Board

Miniature Python-based TfL Arrivals Board Running via Raspberry Pi Zero W

![](assets/img/train-approaching.gif)

## Project Details
I created a thread on Twitter with a video of the arrivals board in action, along with some additional details on how I created it.

[Twitter - TfL Arrival Board Thread ](https://twitter.com/petykowski_/status/1251173895547359234) 

## Configuration
**config.py**

A `config.py` file is required in order to run the arrivals board code. Please review the `config_example.py` file for further details on the required details. Copy `src/config_example.py` to `src/config.py` and populate the values as needed.

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