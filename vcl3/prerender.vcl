#
# NOTE: Heroku/ELB domains resolve to multiple IP addresses and Varnish
# doesn't like this. The backend host must be a single IP address, a
# hostname that resolves to a single IP address, or a dynamically-
# generated director similar to the one described here:
#
# http://blog.cloudreach.co.uk/2013/01/varnish-and-autoscaling-love-story.html
#
import std;

include "prerender_backend.vcl";

sub vcl_recv {
    if (req.url ~ "_escaped_fragment_|prerender=1" ||
         req.http.user-agent ~ "baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot") {

        if (req.http.user-agent ~ "Prerender") {
            return(pass);
        }

        # FIXME: Add a whitelist of files or filetypes to never prerender

        set req.backend = prerender;
        set req.http.Host = "service.prerender.io";
        set req.http.X-Real-IP = client.ip;
        set req.http.X-Forwarded-For = client.ip;

        # If you're using hosted prerender.io, set your token here to enable
        # stat collection.
        #
        # IMPORTANT: This information is cached for the lifespan of
        # the Varnish daemon. If you change your token, you must restart Varnish.
        #
        # FIXME: This would ideally be handled via environment variables but
        # I don't think that environment variables are available in Varnish.
        set req.http.X-Prerender-Token = std.fileread("/etc/varnish/prerender_token.txt");

        # When doing SSL offloading in front of Varnish, set X-Scheme header
        # to "https" before passing the request to Varnish
        if (req.http.X-Scheme !~ "^http(s?)") {
            set req.http.X-Scheme = "http";
        }
        set req.url = "/" + req.http.X-Scheme + "://" + req.http.Host + req.url;

        return(lookup);
    }
}

sub vcl_fetch {
    if (req.backend == prerender) {
        # Set the Varnish cache timeout for rendered content
        set beresp.ttl = 60m;
    }
}
