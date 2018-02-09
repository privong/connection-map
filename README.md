# Connection Map

Examine the list of open IP sockets and use IP geolocation to map where the connections are ostensibly terminating.

## Requirements

The following python modules are used:

* [numpy](http://www.numpy.org)
* [matplotlib](https://matplotlib.org)
* [cartopy](http://scitools.org.uk/cartopy/)
* [GeoIP](https://pypi.python.org/pypi/GeoIP)

The code also assumes the existence of the `ss` ("socket statistics"?) utility and defaults to only exploring IPv4 connections.
