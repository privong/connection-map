#!/usr/bin/env python
"""
Periodically get a list of IP Connections and map them out.

Copyright 2017 George C. Privon
"""

import subprocess
import socket
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import GeoIP


def init():
    """
    Initialiation routine
    """

    gi = GeoIP.open("/usr/share/GeoIP/GeoIPCity.dat", GeoIP.GEOIP_STANDARD)

    return gi


def plot_connections(positions):
    """
    Map the locations of the various connections.
    """

    fig = plt.figure(figsize=(16, 12))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()

    ax.scatter(positions['lon'],
               positions['lat'],
               marker='o',
               transform=ccrs.PlateCarree())
    ax.set_global()
    ax.gridlines(draw_labels=True)
    ax.set_title(socket.gethostname() + ' connections',
                 fontsize='xx-large')
    fig.savefig('connection_map.png', bbox_inches='tight')


def main():
    """
    top-level routine
    """

    gi = init()

    sockinfo = subprocess.run(['ss', '-4'],
                              stdout=subprocess.PIPE)

    if sockinfo.returncode:
        sys.stderr.write("There was a problem running 'ss -4'.\n")

    conns = sockinfo.stdout.decode().split('\n')

    positions = []

    first = True

    for conn in conns:
        conn = conn.split()
        if first:
            first = False
            continue
        if len(conn) == 0:
            continue
        raddr = conn[-1].split(':')[0]

        gir = gi.record_by_addr(raddr)
        positions.append((gir['latitude'],
                          gir['longitude']))

    positions = np.array(positions,
                         dtype=[('lat', float),
                                ('lon', float)])

    plot_connections(positions)

if __name__ == "__main__":
    main()
