# prerender-varnish

prerender-varnish is a Varnish configuration for serving pre-rendered HTML from Javascript pages/apps using [prerender.io](http://prerender.io/).

## Using prerender-varnish

To use prerender-varnish, symlink `prerender.vcl` and `prerender_backend.vcl` in your Varnish configuration directory (usually `/etc/varnish`) and add them to your primary Varnish configuration file:

```c
include "prerender.vcl";
```

## Updating prerender.io backend

The prerender.io rendering service is hosted on Heroku and Heroku (and AWS ELB) domains resolve to multiple IP addresses. Varnish requires backend hosts to resolve to a single IP address. As a workaround, `backend_generator.py` will query DNS for the prerender.io rendering service, generate a Varnish director containing all rendering service IP addresses, write it to `prerender_backend.vcl`, and reload Varnish when the configuration changes.

Run `backend_generator.py` as follows:

```bash
VARNISH_SECRET=xxxxxxx python backend_generator.py [host] [port]
```

With TTLs for these DNS records set quite low, it is advised to run this very frequently. Once per minute should be sufficient.
