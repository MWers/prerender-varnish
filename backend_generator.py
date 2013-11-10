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

import socket

# TODO: Check to see if these were passed as arguments
domain = "prerender.herokuapp.com"
port = 80

TEMPLATE_NODE = '''
{.backend = {.host = "%s";.port = "%s";}.weight = 1;}
'''
# TEMPLATE_NODE = '''    {
#         .backend = {
#             .host = "%s";
#             .port = "80";
#         }
#         .weight = 1;
#     }
# '''

TEMPLATE_DIRECTOR = '''director prerender random {
%s
}'''

(_, _, addrs) = socket.gethostbyname_ex(domain)

# TODO: Check for duplicate addresses

# FIXME: Determine why these strings are being improperly output
nodes = ''.join([repr(TEMPLATE_NODE % (addr, port)) for addr in addrs])
print TEMPLATE_DIRECTOR % nodes
