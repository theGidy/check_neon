#!/usr/bin/env python

# COPYRIGHT
#
# This software is Copyright (c)  2011 NETWAYS GmbH, Gunnar Beutner
#                                 <support@netways.de>
#
# (Except where explicitly superseded by other copyright notices)
#
# LICENSE
#
# This work is made available to you under the terms of Version 2 of
# the GNU General Public License. A copy of that license should have
# been provided with this software, but in any event can be snarfed
# from http://www.fsf.org.
#
# This work is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 or visit their web page on the internet at
# http://www.fsf.org.
#
#
# CONTRIBUTION SUBMISSION POLICY:
#
# (The following paragraph is not intended to limit the rights granted
# to you to modify and distribute this software under the terms of
# the GNU General Public License and is only of importance to you if
# you choose to contribute your changes and enhancements to the
# community by submitting them to NETWAYS GmbH.)
#
# By intentionally submitting any modifications, corrections or
# derivatives to this work, or any other work intended for use with
# this Software, to NETWAYS GmbH, you confirm that
# you are the copyright holder for those contributions and you grant
# NETWAYS GmbH a nonexclusive, worldwide, irrevocable,
# royalty-free, perpetual, license to use, copy, create derivative
# works based on those contributions, and sublicense and distribute
# those contributions and any derivatives thereof.
#
# Nagios and the Nagios logo are registered trademarks of Ethan Galstad.

import sys
import nagiosplugin
import urllib2
from optparse import OptionParser
from xml.dom import minidom

__version__ = '0.1'

class DataContainer:
    """ Container class to fetch data from device
    """
    def __init__(self, host, timeout=4):
        """ Create a new container
            Args:
                host (str): IP or hostname
                timeout (int): Timeout in seconds
        """
        self.url = 'http://' + host + '/values.xml'
        self.timeout = timeout

    def getText(self, nodelist):
        """ Convert XML text nodes into strings
            Args:
                nodelist (DOM nodelist): A node with sub nodes
        """
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ((''.join(rc)).strip()).encode('ascii')

    def parse_nodes(self, target, nodes):
        """ Parse nodes into a dict
            Args:
                target (dict): Target list (for recursive parsing)
                nodes (DOM nodelist: List of elements to parse
        """
        for node in nodes:
            if node.nodeType == minidom.Node.ELEMENT_NODE:
                lowername = (node.nodeName.lower()).encode('ascii')
                if node.childNodes.length == 1:
                    try:
                        target[lowername] = self.getText(node.childNodes)
                    except AttributeError:
                        pass
                else:
                    target[lowername] = {}
                    self.parse_nodes(target[lowername], node.childNodes)

    def get_values(self):
        """ Return a dict of data from device
        """
        f = urllib2.urlopen(self.url, None, self.timeout)
        document = minidom.parse(f)
        root = document.getElementsByTagName('root')[0]
        target = {}
        self.parse_nodes(target, root.childNodes)
        return target

    def print_processor(self, values):
        """ Helper to print values
            Args:
                values (dict)
        """
        later = {}
        for key,value in sorted(values.items()):
            if type(value) is dict:
                later[key] = value
            else:
                print('%-20s: %s' % (key, value,))

        for key,value in sorted(later.items()):
            print("")
            print("Sensor " + key)
            print('-' * 21)
            self.print_processor(value)

    def print_values(self):
        """ Print device information to stdout
        """
        print('Device information:')
        print('-' * 21)
        self.print_processor(self.get_values())

class Neon(nagiosplugin.Resource):
    """ Resource for nagiosplugin
    """
    def __init__(self, temp, hum):
        """ Create a new Neon resource
            Args:
                temp (dict): Dict of temperature values
                hum (dict): Dict of humidity values
        """
        self.temp = temp
        self.hum = hum
    def probe(self):
        """ Probe for plugin values
        """
        yield nagiosplugin.Metric('temperature', float(self.temp['value']))
        yield nagiosplugin.Metric('humidity', float(self.hum['value']))

class NeonSummary(nagiosplugin.Summary):
    """ Building some text for the output
    """
    def __init__(self, temp, hum):
        """ Create a new summary object
            Args
                temp (dict): Dict of temperature values
                hum (dict): Dict of humidity values
        """
        self.temp = temp
        self.hum = hum
    def ok(self, results):
        """ Text message for okay results
            Args:
                resource (nagiosplugin ResourceContainer): Results
        """
        return '{0} {1}, {2} {3}'.format(
            str(results['temperature']),
            self.temp['unit'],
            str(results['humidity']),
            self.hum['unit'],)

@nagiosplugin.guarded
def main():
    """ Main execution function
    """
    parser = OptionParser(usage='%prog --host=<ip|hostname>')

    parser.add_option('-H', '--host', dest='hostname',
                      help='Hostname of the device')

    parser.add_option('-I', '--info', dest='info', action='store_true',
                      help='Display device information')

    parser.add_option('-w', '--warning', dest='warning', metavar='RANGE',
                      help='Temperature Warning threshold (optional)')

    parser.add_option('-c', '--critical', dest='critical', metavar='RANGE',
                      help='Temperature Critical threshold (optional)')

    parser.add_option('-x', '--humiditywarning', dest='humiditywarning', metavar='RANGE',
                      help='Humidity Warning threshold (optional)')

    parser.add_option('-d', '--humiditycritical', dest='humiditycritical', metavar='RANGE',
                      help='Humidity Critical threshold (optional)')

    parser.add_option('-T', '--timeout', dest='timeout', default=4, type='int',
                      help='Timeout for http requests')

    (options, args) = parser.parse_args()

    if options.hostname is None:
        parser.error('Option --host is mandatory')

    container = DataContainer(options.hostname, options.timeout)

    if options.info:
        container.print_values()
        return 3

    try:
        values = container.get_values()
    except urllib2.URLError as e:
        raise nagiosplugin.CheckError(e.reason)

    temperature_warn = None
    temperature_critical = None
    humidity_warn = None
    humidity_critical = None

    # Using default thresholds configured in the web interface
    if not options.warning:
        temperature_warn = values['temperature']['lowalarm'] + ':' + values['temperature']['highalarm']
    else:
        temperature_warn = options.warning

    if not options.humiditywarning:
        humidity_warn = values['humidity']['lowalarm'] + ':' + values['humidity']['highalarm']
    else:
        humidity_warn = options.humiditywarning

    if not options.critical:
        temperature_critical = values['temperature']['lowalarm'] + ':' + values['temperature']['highalarm']
    else:
        temperature_critical = options.critical

    if not options.humiditycritical:
        humidity_critical = values['humidity']['lowalarm'] + ':' + values['humidity']['highalarm']
    else:
        humidity_critical = options.humiditycritical

    check = nagiosplugin.Check(
        Neon(values['temperature'], values['humidity']),
        nagiosplugin.ScalarContext('temperature',
                                   temperature_warn,
                                   temperature_critical),
        nagiosplugin.ScalarContext('humidity',
                                   humidity_warn,
                                   humidity_critical),
        NeonSummary(values['temperature'], values['humidity']))

    return check.main()

if __name__ == '__main__':
    sys.exit(main())
