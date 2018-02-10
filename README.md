# Connection Map

Examine the list of open IP sockets and use IP geolocation to map where the connections are ostensibly terminating.

## Requirements

The following python modules are used:

* [numpy](http://www.numpy.org)
* [matplotlib](https://matplotlib.org)
* [cartopy](http://scitools.org.uk/cartopy/)
* [geoip2](https://pypi.python.org/pypi/geoip2)

The code assumes the existence of the `ss` ("socket statistics"?) utility and defaults to only exploring IPv4 connections.

You will also need to install the [MaxMind GeoLite2 database](http://dev.maxmind.com/geoip/geoip2/geolite2/).

## Usage

To make a map of the current connections issue the following command:

```
$ python connection_map.py
```

This will create a `connection_map.png` image showing the terminating locations of currently open connections on your machine.

Note that the location of the `GeoLite2` database is hard-coded in the `init()` function; you may need to change this to suit your system configuration.
