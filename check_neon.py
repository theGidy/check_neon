#!/usr/bin/python

import sys
import nagiosplugin
import urllib2

from optparse import OptionParser
from xml.dom import minidom

class DataContainer:
    def __init__(self, host, timeout=4):
        self.url = 'http://' + host + '/values.xml'
        self.timeout = timeout

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ((''.join(rc)).strip()).encode('ascii')

    def parse_nodes(self, target, nodes):
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
        f = urllib2.urlopen(self.url, None, self.timeout)
        document = minidom.parse(f)
        root = document.getElementsByTagName('root')[0]
        target = {}
        self.parse_nodes(target, root.childNodes)
        return target

    def print_processor(self, values):
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
        print('Device information:')
        print('-' * 21)
        self.print_processor(self.get_values())

class Neon(nagiosplugin.Resource):
    def __init__(self, temp, hum):
        self.temp = temp
        self.hum = hum
    def probe(self):
        yield nagiosplugin.Metric('temperature', float(self.temp['value']))
        yield nagiosplugin.Metric('humidity', float(self.hum['value']))

class NeonSummary(nagiosplugin.Summary):
    def __init__(self, temp, hum):
        self.temp = temp
        self.hum = hum
    def ok(self, results):
        return '{0} {1}, {2} {3}'.format(
            str(results['temperature']),
            self.temp['unit'],
            str(results['humidity']),
            self.hum['unit'],)

@nagiosplugin.guarded
def main():
    parser = OptionParser()

    parser.add_option('-H', '--host', dest='hostname',
                      help='Hostname of the device')

    parser.add_option('-I', '--info', dest='info', action='store_true',
                      help='Display device information')

    parser.add_option('-w', '--warning', dest='warning', metavar='RANGE',
                      help='Warning threshold (optional)')

    parser.add_option('-c', '--critical', dest='critical', metavar='RANGE',
                      help='Critical threshold (optional)')

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

    if not options.warning:
        temperature_warn = values['temperature']['lowalarm'] + ':' + values['temperature']['highalarm']
        humidity_warn = values['humidity']['lowalarm'] + ':' + values['humidity']['highalarm']
    else:
        temperature_warn = options.warning
        humidity_warn = options.warning

    if not options.critical:
        temperature_critical = values['temperature']['lowalarm'] + ':' + values['temperature']['highalarm']
        humidity_critical = values['humidity']['lowalarm'] + ':' + values['humidity']['highalarm']
    else:
        temperature_critical = options.critical
        humidity_critical = options.critical

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