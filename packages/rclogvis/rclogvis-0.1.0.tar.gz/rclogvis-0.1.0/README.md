# RCLogVis: Log visualistion for EdgeTX radios #

This repository contains software to visualise the flight telemetry data from drones (e.g. multi rotors or fixed wings) by EdgeTX remote control radios.

## Author ##

The software is primarily developed and maintained by Fabian Jankowski. For more information feel free to contact me via: fabian.jankowski at cnrs-orleans.fr.

## Installation ##

The easiest and recommended way to install the software is via the Python command `pip` directly from the `rclogvis` GitHub software repository. For instance, to install the master branch of the code, use the following command:  
`pip install git+https://github.com/fjankowsk/rclogvis.git@master`

This will automatically install all dependencies. Depending on your Python installation, you might want to replace `pip` with `pip3` in the above command.

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
