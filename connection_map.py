#!/usr/bin/env python
"""
Periodically get a list of IP Connections and map them out.

Some code from the cartopy documentation.
http://scitools.org.uk/cartopy/docs/latest/

Other code Copyright 2017 George C. Privon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import socket
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
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
    ax.set_global()

    countries = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='50m',
        facecolor='none')

    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')

    SOURCE = 'Natural Earth'
    LICENSE = 'public domain'

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(countries, edgecolor='gray')
    ax.add_feature(states_provinces, edgecolor='gray')

    ax.gridlines(draw_labels=True)

    ax.scatter(positions['lon'],
               positions['lat'],
               marker='o',
               color='green',
               transform=ccrs.PlateCarree(),
               zorder=20)

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
