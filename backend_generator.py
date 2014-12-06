#!/usr/bin/env python

#
# Script uses the following flow:
# - Hash existing prerender_backend.vcl file contents
# - Get ip addresses for rendering backend
# - Make sure that there was at least one ip address returned
# - Build backend node array
# - Add backend node array to director
# - Hash generated director
# - If hashes differ:
#     - Update prerender_backend.vcl
#     - Reload Varnish configuration
# - Notify on any errors
#
# TODO: Add logging
# TODO: Add notifications
# TODO: Add error checking
#

import hashlib
import optparse
import os
import socket
import sys

desc = """Generate a Varnish backend configuration given a hostname."""

parser = optparse.OptionParser(description=desc)
parser.add_option('-n', '--hostname',
                  dest='hostname',
                  help='prerender.io rendering backend hostname '
                       '[default: %default]',
                  default='service.prerender.io')
parser.add_option('-p', '--port',
                  dest='port',
                  help='prerender.io rendering backend port '
                       '[default: %default]',
                  type='int',
                  default=80)
parser.add_option('-d', '--dest',
                  dest='backend_conf',
                  help='varnish backend conf file to overwrite '
                       '[default: %default]',
                  default='/etc/varnish/prerender_backend.vcl')
parser.add_option('-r', '--reload-varnish',
                  action='store_true',
                  dest='reloadvarnish',
                  help='reload varnish on completion '
                       '[default: %default]',
                  default=False)
parser.add_option('-v', '--verbose',
                  action='store_true',
                  dest='verbose',
                  help='show verbose output '
                       '[default: %default]',
                  default=False)
parser.add_option('--dry-run',
                  action='store_true',
                  dest='dry_run',
                  help='don\'t write to conf file or reload Varnish '
                       '[default: %default]',
                  default=False)
(opts, args) = parser.parse_args()

TPL_NODE = '''    {
        .backend = {
            .host = "%s";
            .port = "%d";
        }
        .weight = 1;
    }
'''

TPL_DIRECTOR = '''director prerender random {
%s}
'''

# Get ip addresses for rendering backend
(_, _, rawaddrs) = socket.gethostbyname_ex(opts.hostname)
rawaddrs.sort()
addrs = set(rawaddrs)

# Make sure that there was at least one ip address returned
if not addrs:
    # TODO: Send some sort of notification here.
    print ("The hostname '%s' did not resolve to any IP addresses." %
           opts.hostname)
    sys.exit(1)

# Build backend node array and director
nodes = ''.join([(TPL_NODE % (addr, opts.port)) for addr in addrs])
director = TPL_DIRECTOR % (nodes)

# Compare generated director to existing director
try:
    filehash = hashlib.sha256(open(opts.backend_conf, 'rb').read()).hexdigest()
except IOError:
    # Assume no file exists and set hash to '' so that it wil be created
    filehash = ''
stringhash = hashlib.sha256(director).hexdigest()

if filehash != stringhash:
    if not opts.dry_run:
        backend_conf = open(opts.backend_conf, 'w')
        backend_conf.write(director)
        backend_conf.close()

        if opts.verbose:
            print "Updated backend configuration"
    else:
        if opts.verbose:
            print ("Backend configuration in %s differs from generated "
                   "director" % (opts.backend_conf))

    # Reload Varnish configuration
    if opts.reloadvarnish:
        if opts.verbose:
            print "Checking Varnish configuration"
        if os.system('service varnish configtest') == 0:
            if opts.verbose:
                print "Reloading Varnish"
            os.system('service varnish reload')

if opts.verbose:
    print "Generated Varnish conf:"
    print director
