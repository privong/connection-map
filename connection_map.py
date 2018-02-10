#!/usr/bin/env python
"""
Get a list of IP Connections and map them out.

Some code from the cartopy documentation.
http://scitools.org.uk/cartopy/docs/latest/

Other code Copyright 2017-2018 George C. Privon

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
import argparse
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import geoip2.database as ipdb


def getArgs():
    """
    Command line arguments
    """

    parser = argparse.ArgumentParser(description="Get open connections, \
geolocate IP addresses, and make a map of the connection endpoints.")

    parser.add_argument('-4', '--ipv4', default=False, action='store_true',
                        help="Geolocate IPv4 connections.")
    parser.add_argument('-6', '--ipv6', default=False, action='store_true',
                        help="Geolocate IPv6 connections.")

    args = parser.parse_args()

    if not args.ipv4 and not args.ipv6:
        # if nothing was specified, default to IPv4 only
        args.ipv4 = True

    return args


def init(ip):
    """
    Initialiation routine
    """

    if ip == 4:
        gi = ipdb.Reader("/usr/share/GeoIP/GeoLite2-City.mmdb")
    elif ip == 6:
        # FIXME: this doesn't work for IPv6
        gi = ipdb.Reader("/usr/share/GeoIP/GeoLite2-City.mmdb")

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

    for ipType in np.unique(positions['iptype']):
        valid = positions['iptype'] == ipType
        ax.scatter(positions['lon'][valid],
                   positions['lat'][valid],
                   marker='o',
                   transform=ccrs.PlateCarree(),
                   zorder=20,
                   label='IPv{0:1.0f}'.format(ipType))

    ax.set_title(socket.gethostname() + ' connections',
                 fontsize='xx-large')
    ax.legend(loc='best')
    fig.savefig('connection_map.png', bbox_inches='tight')


def checkLocal(IP, iptype):
    """
    Check to see if the IP address is in the IPv4/IPv6 private blocks.
    Returns True if the address is local.

    """

    if iptype == 4:
        if IP == '127.0.0.1':
            return True
        ips = IP.split('.')

        if int(ips[0]) == 10:
            return True
        elif int(ips[0]) == 192 and int(ips[1]) == 168:
            return True
        elif int(ips[0]) == 172 and (int(ips[1]) >= 16 and int(ips[1]) <= 31):
            return True
    elif iptype == 6:
        ips = IP.split(':')
        if re.match('fd', ips[0][0:2], re.IGNORECASE):
            return True

    return False


def main():
    """
    top-level routine
    """

    args = getArgs()
    iplist = []
    if args.ipv4:
        iplist.append(4)
    if args.ipv6:
        iplist.append(6)

    positions = []

    for ip in iplist:
        gi = init(ip)

        sockinfo = subprocess.run(['ss', '-{0:1.0f}'.format(ip)],
                                  stdout=subprocess.PIPE)

        if sockinfo.returncode:
            sys.stderr.write("There was a problem running 'ss -{0:1.0f}'.\n".format(ip))

        conns = sockinfo.stdout.decode().split('\n')

        # skip the header line of ss
        first = True

        for conn in conns:
            conn = conn.split()
            if first:
                first = False
                continue
            if len(conn) == 0:
                continue
            raddr = conn[-1].split(':')[0]

            if checkLocal(raddr, ip):
                continue

            try:
                gir = gi.city(raddr)
            except:
                sys.stderr.write(raddr + " not found. skipping.\n")
            try:
                positions.append((gir.location.latitude,
                                  gir.location.longitude,
                                  ip))
            except TypeError:
                sys.stdout.write('No position for ' + raddr + '\n')

    positions = np.array(positions,
                         dtype=[('lat', float),
                                ('lon', float),
                                ('iptype', float)])

    plot_connections(positions)

if __name__ == "__main__":
    main()
