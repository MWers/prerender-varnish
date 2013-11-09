import socket
 
domain = "prerender.herokuapp.com"
 
TEMPLATE_NODE = '''    {
        .backend = {
            .host = "%s";
            .port = "80";
        }
        .weight = 1;
    }
'''
 
TEMPLATE_DIR = '''director prerender random {
%s
}'''
 
# FIXME: Make this more pythonic
(_, _, addr) = socket.gethostbyname_ex(domain)
nodes = ""
for i in range(len(addr)):
    nodes = nodes + TEMPLATE_NODE % (addr[i])
print TEMPLATE_DIR % nodes