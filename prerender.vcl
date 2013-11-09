#
# NOTE: Heroku/ELB domains resolve to multiple IP addresses and Varnish
# doesn't like this. The backend host must be a single IP address, a 
# hostname that resolves to a single IP address, or a dynamically-
# generated director similar to the one described here:
#
# http://blog.cloudreach.co.uk/2013/01/varnish-and-autoscaling-love-story.html
#
 
backend prerender {
    # .host = "prerender.herokuapp.com";
    .host = "23.21.166.91";
    .port = "80";
}
 
sub vcl_recv {
    if (req.url ~ "_escaped_fragment_|prerender=1" ||
         req.http.user-agent ~ "googlebot|yahoo|bingbot|baiduspider|yandex|yeti|yodaobot|gigabot|ia_archiver|facebookexternalhit|twitterbot|developers\.google\.com") {

        if (req.http.user-agent ~ "Prerender") {
            return(pass);
        }
 
        set req.backend = prerender;
 
        # When doing SSL offloading in front of Varnish, set X-Scheme header
        # to "https" before passing the request to Varnish
        if (req.http.X-Scheme !~ "^http(s?)") {
            set req.http.X-Scheme = "http";
        }
        set req.url = "/" + req.http.X-Scheme + "://" + req.http.Host + req.url;
 
        return(lookup);
    }
}
 
sub vcl_miss {
    if (req.backend == prerender) {
        set bereq.http.Host = "prerender.herokuapp.com";
        set bereq.http.X-Real-IP = client.ip;
        set bereq.http.X-Forwarded-For = client.ip;
    }
}
 
sub vcl_fetch {
    if (req.backend == prerender) {
        # Set the Varnish cache timeout for rendered content
        set beresp.ttl = 60m;
    }
}