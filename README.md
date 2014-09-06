Plugin: check_neon
==================

This is a ICINGA/NAGIOS plugin for the Neon 100 device which is manufactured by Sensormetrix.

Behind the scenes
-----------------

The plugin just fech the xml data from the device and probe for thresholds.

Installation
------------

Installation is just simple. You need Python >= 2.6 to run this.

### Python Setuptools

To install nagiosplugins python package you need Python Setuptools. Just make sure to have that installed. For RHEL or
CentOS you can simply run

    # yum install python-setuptools.noarch

### nagiosplugin Module

You need the Python nagiosplugin package. More information can be found on

* [Package website](http://pythonhosted.org/nagiosplugin/index.html)
* [PyPi repository](https://pypi.python.org/pypi/nagiosplugin/)

Extract the package, go into the directory and type

    # wget https://pypi.python.org/packages/source/n/nagiosplugin/nagiosplugin-1.2.1.tar.gz#md5=d81c724525e8e8b290d17046109e71d2
    # cd nagiosplugin-1.2.1
    # python setup.py install

### check_neon

Move the check_neon.py script to your favorite ICINGA resource directory, e.g.

    # cp check_neon.py /usr/local/icinga/libexec

Usage
-----

First, you should try that everything is working:

    # ./check_neon.py --host=X.X.X.X  --info
    Device information:
    ---------------------
    dhcp                : 1
    dst                 : 0
    gmtoffset           : 0
    ipaddress           : X.X.X.X
    mac                 : FF:FF:FF:FF:FF:FF
    netmask             : 255.255.0.0
    powerup             : 21 days, 3 hrs, 49 min, 51 sec
    productname         : Neon110
    serialnumber        : 036030
    time                : 03:30:33 PM
    unitname            : Neon110
    version             : V1.4

    Sensor humidity
    ---------------------
    alarm               : 0
    highalarm           : 80
    lowalarm            : 20
    unit                : %RH
    value               : 30.67

    Sensor temperature
    ---------------------
    alarm               : 0
    highalarm           : 25
    lowalarm            : 0
    unit                : C
    value               : 21.14

Probe device
------------

Just type this:

    # ./check_neon.py --host=10.0.10.81
    NEON OK - temperature is 21.14 C, humidity is 30.52 %RH
    | humidity=30.52;20:80;20:80 temperature=21.14;25;25

We check temperature and humidity always together. If you to not set critical or warning thresholds we'll use the
Hi- and LoAlarm from webinterface

Probe with own thresholds:

    # ./check_neon.py --host=10.0.10.81 -c 20
    NEON CRITICAL - temperature is 21.15 (outside range 0:20)
    critical: temperature is 21.15 (outside range 0:20)
    critical: humidity is 30.33 (outside range 0:20)
    | humidity=30.33;20:80;20 temperature=21.15;25;20

### Program switches:

Simple usage: **./check_neon.py --host=<hostname | ip address>**

**-h | --help**

Displays a small help screen and exit

**-H | --host=<STRING>**

Device target. This could be an ip adress of a dns hostname

**-w | --warning=<RANGE>**

Threshold for warning state. Have a look on the nagios plugin development guidelines
[here](https://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT)

**-c | --critical=<RANGE>**

Threshold for critical state. Have a look on the nagios plugin development guidelines
[here](https://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT)

**-T | --timeout=<int>**

Timeout in seconds for http requests to get the data from device

Copyright
---------

Copyright (c) 2014 NETWAYS GmbH

[www.netways.de](http://www.netways.de)

info@netways.de

Where to buy
------------

Product can be found here:
[NETWAYS Shop](http://shop.netways.de/ueberwachung/sequoia/messgerate/neon-110-netzwerksensor-fur-temperatur-und-luftfeuchtigkeit.html)

Bugs and repository
-------------------

For chorus of praise or complaints you can go here:

* [https://git.netways.org/plugins/check_neon](https://git.netways.org/plugins/check_neon)
* [https://www.netways.org/projects/plugins](https://www.netways.org/projects/plugins)

Native git access: git://git.netways.org/plugins/check_neon.git
