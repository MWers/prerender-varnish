#!/usr/bin/env python

#
# TODO: Build out script using the following flow:
# - Fingerprint existing prerender_backend.vcl file contents
# - Get ip addresses for rendering backend
# - Make sure that there was at least one ip address returned
# - Build backend node array
# - Add backend node array to director
# - Fingerprint generated director
# - If fingerprints differ:
#     - Update prerender_backend.vcl
#     - Reload Varnish configuration
# - Notify on any errors
#

import optparse
import socket

desc = """Generate a Varnish backend configuration given a hostname."""


parser = optparse.OptionParser(description=desc)
parser.add_option('--hostname',
                  dest='hostname',
                  help='prerender.io rendering backend hostname',
                  default='prerender.herokuapp.com')
parser.add_option('-p', '--port',
                  dest='port',
                  help='prerender.io rendering backend port',
                  type='int',
                  default=80)
parser.add_option('-d', '--dest',
                  dest='varnish_backend_conf',
                  help='varnish backend configuration file to overwrite',
                  default='/etc/varnish/prerender_backend.vcl')
parser.add_option('--dry-run',
                  action='store_true',
                  dest='dry_run',
                  help='output to stdout, don\'t write to conf file',
                  default=False)
(opts, args) = parser.parse_args()

# TEMPLATE_NODE = '''
# {.backend = {.host = "%s";.port = "%s";}.weight = 1;}
# '''
TEMPLATE_NODE = '''    {
        .backend = {
            .host = "%s";
            .port = %d;
        }
        .weight = 1;
    }
'''

TEMPLATE_DIRECTOR = '''director prerender random {
%s}'''

(_, _, addrs) = socket.gethostbyname_ex(opts.hostname)

# TODO: Check for duplicate addresses

# FIXME: Determine why these strings are being improperly output
nodes = ''.join([(TEMPLATE_NODE % (addr, opts.port)) for addr in addrs])
print TEMPLATE_DIRECTOR % nodes


def main():
    return
    # generate_homepages()
    # copy_to_working_dir()
    # customize_for_servers()
    # deploy_to_production()
    # log_generation()


if __name__ == '__main__':
    main()
