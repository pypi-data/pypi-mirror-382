# RCLogVis: Log visualistion for EdgeTX radios #

This repository contains software to visualise the flight telemetry data from drones (e.g. multi rotors or fixed wings) by EdgeTX remote control radios.

## Author ##

The software is primarily developed and maintained by Fabian Jankowski. For more information feel free to contact me via: fabian.jankowski at cnrs-orleans.fr.

## Installation ##

The easiest and recommended way to install the software is via the Python command `pip` directly from the `rclogvis` GitHub software repository. For instance, to install the master branch of the code, use the following command:  
`pip install git+https://github.com/fjankowsk/rclogvis.git@master`

This will automatically install all dependencies. Depending on your Python installation, you might want to replace `pip` with `pip3` in the above command.

## Prerequisites ##

`rclogvis` analyses drone telemetry data recorded by EdgeTX/OpenTX remote control handsets and saved in comma-separated values (CSV) format files. For instance, Betaflight transmits several telemetry parameters via ExpressLRS or other radio link protocols to the RC handset. These typically include information about the RC link quality, drone attitude, power consumption, and eventually GPS data such as position, speed, altitude and heading.

As a first step, you must discover all the available telemetry sensors in your EdgeTX remote control handset. This is done on the model's telemetry page under Model -> Telemetry -> Sensors.

Once that is done, you must configure the logging of the telemetry data to the RC handset's internal storage or SD card. This is achieved by adding a special function with the "SD Logs" action on the radio, located under Model -> Special Functions. This function should become active when the drone is armed, i.e. when the arm switch is activated. The logging interval depends on the telemetry update rate via the RC link. In particular, it should be slower than the telemetry update rate. For ExpressLRS, the telemetry packet intervals for different link configurations are available on the [telemetry bandwidth page](https://www.expresslrs.org/info/telem-bandwidth/). In practice, a logging interval of 0.2 - 0.3 seconds works well for a standard 150 Hz ExpressLRS link setup.

The telemetry log files will appear in the "LOGS" directory on the RC handset's SD card after the first flight and can be downloaded from there by connecting a USB cable.

## Usage ##

```console
$ rclogvis-plot -h
usage: rclogvis-plot [-h] filename

Plot telemetry log data.

positional arguments:
  filename    Filename to process.

options:
  -h, --help  show this help message and exit
```

`Filename` is a CSV file with the telemetry logging output from the EdgeTX or OpenTX radio remote control handset.

## GPX File Export ##

`rclogvis` converts the GPS information in the telemetry logs into a GPX file that can be visualised using more sophisticated GIS tools, such as [qmapshack](https://github.com/Maproom/qmapshack) or Google Earth. It creates a file called "export.gpx" in the current working directory by default.
