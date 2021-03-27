

<center>
<img src="snowdriftLogo.png" />
</center>

# About

Snowdrift is a forecast model component for snowdrift prediction,
originally developed by **Vegsýn** and the **Icelandic Meteorological Office**
as part of the **SNAPS** northern perimetry project.

## Quickstart

```sh
# install deps, if not already installed
$ sudo apt-get install libeccodes-dev git feh
$ sudo pip3 install numpy pygrib pillow trollimage nose mkdocs
# get the software project
$ git clone "https://github.com/...."
$ cd snowdrift
$ export PYTHONPATH=$PWD
# run tests - will also download a test
# forecast in './tests/testdata/' directory
$ python3 -m "nose" -v ./tests/
# generate some snowdrift images from test data,
$ bin/snowdrift tests/testdata/harmonie* --out imgs/test --format PNG
# loop through the resulting images,
$ feh -D 0.3 imgs/test*
# generate a snowdrift forecast in GRIB format
$ bin/snowdrift tests/testdata/harmonie* --out snowdrift.grb --format GRIB
```
<center>
<img src="animation.gif" style="width:60%; border: 1px solid lightgray;"/>
</center>

## Installation
The software requires `python3` and installation of the following packages:

```sh
# ECMWF grid decoder library
$ sudo apt-get install libeccodes-dev git
# python modules from pip
$ sudo pip3 install numpy pygrib pillow trollimage nose mkdocs
```

Install the snowdrift module with pip,
```sh
$ sudo pip3 install "git+....."
```

With setup tools can alternatively do,
```sh
$ git clone "https://github.com/...."
$ cd snowdrift
$ sudo python3 setup.py install
```

During development and testing it's not necessary to install the
snowdrift module. In this case you can simply set the `PYTHONPATH` environment variable
to include the snowdrift project folder

```sh
$ cd snowdrift
$ export PYTHONPATH=$PWD:$PYTHONPATH
$ python3
> import snowdrift
# do some coding...
```

## Tests
It is a good idea to run the tests provided with the project in the `tests/` directory.
This helps to confirm that software is working as intended on your platform.

```sh
$ python3 -m "nose" -v ./tests/
```

To capture the standard output from the tests, you can run with `-s` flag,

```sh
python3 -m "nose" -vs ./tests/
```
