# Connection Map

Periodically assess which IP sockets are open and use geolocation to map where the connections are ostensibly terminating.

## Requirements

The following python modules are used:

* numpy
* matplotlib
* cartopy
* GeoIP

The code also assumes the existence of the `ss` ("socket statistics"?) utility and defaults to only exploring IPv4 connections.
